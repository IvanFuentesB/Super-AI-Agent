# Repo Intake Strategy

## Why Not Dump Repos Into Core

Third-party repos are intake material, not core architecture. Dumping them into the main repo makes scope, licensing, and maintenance harder to control.

## Intake Lane

- use `21_repos/third_party` as the intake lane
- keep clones for review, comparison, and wrapper planning only
- do not treat vendor source as first-party project code

## What To Extract Into Core

- patterns worth reusing
- wrapper ideas
- evaluation notes
- adapter plans
- workflow lessons that fit the approval-gated architecture

## Evaluation Criteria

- usefulness
- maintenance quality
- Windows fit
- complexity cost
- safety fit
- licensing fit
