"""Opt-in, synthetic-only local capability. No service or canonical memory."""
from __future__ import annotations

import argparse
import ast
import json
import re
import time
import tracemalloc

MAX_TURNS = 3
MAX_REQUESTS = 4
DEADLINE_SECONDS = 90
MAX_RESPONSE_BYTES = 131072
HOST = "http://127.0.0.1:11434"
REVIEWED_MODELS = frozenset(("gemma3:4b", "qwen3:4b"))
TASK = ("Use calculator twice, in sequence. First compute 17*23+9. "
        "Then use calculator to multiply that result by 2. "
        "Answer only with the final number. /no_think")
SYSTEM = ('For each response, output ONLY one tool call in this format:\n'
          'TOOL: calculator\nINPUT: {"expression": "17*23+9"}\n'
          'Wait for its Observation. Then call calculator with the previous result times 2. '
          'After the second Observation output ONLY FINAL_ANSWER: <number>. '
          'No thoughts, prose, markdown, memory or other tools.')


def select_model(requested: str, installed: list[str]) -> str:
    if not requested or not re.fullmatch(r"[a-zA-Z0-9_.:-]{1,80}", requested):
        raise ValueError("Explicit local model name required")
    if requested not in installed or requested not in REVIEWED_MODELS:
        raise ValueError("Model not installed; no download or cloud fallback")
    return requested


def validate_expression(expression: str) -> None:
    if not isinstance(expression, str) or not expression or len(expression) > 80:
        raise ValueError("Expression size refused")
    if not re.fullmatch(r"[0-9+*() .-]+", expression):
        raise ValueError("Only bounded arithmetic is allowed")
    if "**" in expression or any(len(n) > 9 for n in re.findall(r"\d+", expression)):
        raise ValueError("Unbounded arithmetic refused")


class Budget:
    def __init__(self):
        self.deadline = time.monotonic() + DEADLINE_SECONDS
        self.requests = 0

    def check(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Local evaluation deadline")
        return remaining

    def request(self, request):
        if (str(request.url).split("?", 1)[0] not in (HOST + "/api/tags", HOST + "/api/chat")
                or request.url.query or request.headers.get("authorization")
                or request.method not in ("GET", "POST")):
            raise ValueError("Endpoint or credentials refused")
        self.requests += 1
        if self.requests > MAX_REQUESTS:
            raise TimeoutError("Request budget exhausted")
        remaining = min(20.0, self.check())
        request.extensions["timeout"] = dict(connect=remaining, read=remaining,
                                               write=remaining, pool=remaining)


def local_client(budget, transport=None):
    import httpx

    class LimitedStream(httpx.SyncByteStream):
        def __init__(self, stream):
            self.stream = stream

        def __iter__(self):
            total = 0
            for chunk in self.stream:
                budget.check()
                total += len(chunk)
                if total > MAX_RESPONSE_BYTES:
                    raise ValueError("Response size refused")
                yield chunk
            budget.check()

        def close(self):
            self.stream.close()

    class LimitedTransport(httpx.BaseTransport):
        def __init__(self):
            self.inner = transport or httpx.HTTPTransport(retries=0, trust_env=False)

        def handle_request(self, request):
            response = self.inner.handle_request(request)
            if response.is_redirect or response.headers.get("content-encoding", "identity") != "identity":
                response.close()
                raise ValueError("Redirect or encoded response refused")
            budget.check()
            response.stream = LimitedStream(response.stream)
            return response

        def close(self):
            self.inner.close()

    return httpx.Client(base_url=HOST, transport=LimitedTransport(), trust_env=False,
                        follow_redirects=False, timeout=20,
                        event_hooks={"request": [budget.request]},
                        headers={"Accept-Encoding": "identity"})


def calculator_tool(budget=None, records=None):
    from openjarvis.tools.calculator import CalculatorTool
    from openjarvis.core.types import ToolResult

    class BoundedCalculator(CalculatorTool):
        calls = 0

        def execute(self, **params):
            try:
                if budget is not None:
                    budget.check()
                self.calls += 1
                if self.calls > 4:
                    raise ValueError("Tool budget exhausted")
                if set(params) != {"expression"}:
                    raise ValueError("Unexpected tool arguments")
                validate_expression(params["expression"])
            except ValueError:
                return ToolResult(tool_name="calculator", content="Arithmetic refused", success=False)
            result = super().execute(**params)
            if budget is not None:
                budget.check()
            if records is not None:
                records.append((params["expression"], result.content, result.success))
            return result

        def to_openai_function(self):
            # Avoid loading learned tool-description overrides from a user home.
            spec = self.spec
            return {"type": "function", "function": {"name": spec.name,
                    "description": "Small arithmetic using +, -, *, parentheses only.",
                    "parameters": spec.parameters}}

    return BoundedCalculator()


def verified_sequence(records, answer):
    if len(records) != 2 or answer.strip() not in ("800", "800.0"):
        return False
    for (expression, value, success), expected, number in zip(
            records, ("17*23+9", "400*2"), ("400.0", "800.0")):
        if (not success or value != number or
                ast.dump(ast.parse(expression, mode="eval")) !=
                ast.dump(ast.parse(expected, mode="eval"))):
            return False
    return True


def run_recording_fixture(model: str, transport) -> dict:
    """Offline test seam only. Production live inference is not an exposed capability."""
    import httpx
    if not isinstance(transport, httpx.MockTransport):
        raise ValueError("Only a recording MockTransport is supported before host adoption")
    return _run_agent(model, transport)


def _run_agent(model: str, transport) -> dict:
    import httpx
    if not isinstance(transport, httpx.MockTransport):
        raise ValueError("Live inference is unavailable pending host adoption")
    budget = Budget()
    start = time.monotonic()
    from openjarvis.agents.orchestrator import OrchestratorAgent
    from openjarvis.engine.ollama import OllamaEngine

    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    class MeteredOllama(OllamaEngine):
        def generate(self, *args, **kwargs):
            budget.check()
            result = super().generate(*args, **kwargs)
            budget.check()
            for key in usage:
                usage[key] += result.get("usage", {}).get(key, 0)
            return result

    budget.check()
    tracemalloc.start()
    engine = MeteredOllama(host=HOST, timeout=20)
    engine._client.close()
    engine._client = local_client(budget, transport)
    try:
        response = engine._client.get("/api/tags")
        response.raise_for_status()
        installed = [m["name"] for m in response.json()["models"]]
        selected = select_model(model, installed)
        records = []
        agent = OrchestratorAgent(engine, selected, tools=[calculator_tool(budget, records)],
                                  max_turns=MAX_TURNS, max_tokens=384,
                                  temperature=0.0, parallel_tools=False,
                                  mode="structured", system_prompt=SYSTEM)
        result = agent.run(TASK)
        budget.check()
        verified = (verified_sequence(records, result.content)
                    and not result.metadata.get("max_turns_exceeded"))
        return {"status": "completed" if verified else "uncertain",
                "model": selected, "agent": "orchestrator", "installed_models": installed,
                "answer": 800 if verified else None, "turns": result.turns,
                "verified_steps": [{"expression": expression, "value": float(value)}
                                   for expression, value, _ in records] if verified else [],
                "tool_call_count": len(result.tool_results),
                "usage": usage,
                "elapsed_seconds": round(time.monotonic() - start, 3),
                "http_requests": budget.requests,
                "python_peak_bytes": tracemalloc.get_traced_memory()[1],
                "resource_scope": "Python allocations only; GPU energy and native RSS unmeasured",
                "cloud_used": False, "network_used": False,
                "execution_scope": "offline recording fixture",
                "training_used": False, "canonical_memory_used": False}
    finally:
        engine._client.close()
        tracemalloc.stop()


def evaluate(*, enable=False, model=""):
    if not enable:
        return {"status": "disabled", "inference_used": False,
                "next_action": "Explicit --enable and installed --model required"}
    return {"status": "blocked", "inference_used": False,
            "message": "Hermes must establish a cloud-disabled host policy before live adoption",
            "host_cloud_policy": "not_attested",
            "next_action": "Use the offline fixture tests; no CLI bypass is provided"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--model", default="")
    args = parser.parse_args()
    result = evaluate(enable=args.enable, model=args.model)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in ("disabled", "completed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
