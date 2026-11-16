"""Disposable calculator-only stdio fixture, never registered globally."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from openjarvis_adapter import calculator_tool
from openjarvis.mcp.protocol import MCPRequest
from openjarvis.mcp.server import MCPServer


def main():
    server = MCPServer(tools=[calculator_tool()])
    # One finite test connection; EOF exits without leaving a background service.
    for _ in range(12):
        line = sys.stdin.buffer.readline(65537)
        if not line:
            return
        if len(line) > 65536:
            raise ValueError("Request size refused")
        request = MCPRequest.from_json(line.decode("utf-8"))
        if request.id is None:
            continue
        response = server.handle(request)
        if response is not None:
            print(response.to_json(), flush=True)


if __name__ == "__main__":
    main()
