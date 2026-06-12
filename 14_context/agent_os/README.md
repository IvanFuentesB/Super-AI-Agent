# Agent OS Guard and Local Worker Trial

This folder contains repo-local contracts and example artifacts for the first
Agent OS guard vertical slice.

The Rust guard is default-deny. It validates a proposed local worker action
before the Python harness may render a simulation or suggestion-only plan.
The harness never executes `approved_local`, browser, computer-use, account,
posting, purchase, or model-output-as-command actions.

Folders:

- `requests/`: public-safe example policy requests.
- `trials/`: harmless suggestion-only plan artifacts.
- `runs/`: guard decisions and local run records.
- `handoffs/`: compact pointers for the next human or agent.

Raw approval values are never copied into guard decisions or run records.
