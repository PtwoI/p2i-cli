# p2i-cli

Terminal entry point for local P2I workflows.

## Boundary

Thin commands for `p2i --help`, `p2i serve`, `p2i demo`, and Harness/skill JSON actions. Delegate tracing and validation to [p2i-core](https://github.com/PtwoI/p2i-core); delegate browser serving to [p2i-gui](https://github.com/PtwoI/p2i-gui). Keep established command names and action JSON compatible.

## Migration status

**Repository initialized; CLI code has not been moved yet.** Current commands live in [PtwoI/p2i](https://github.com/PtwoI/p2i): `src/p2i/cli.py`, `src/p2i/harness/cli.py` and `src/p2i/skills/cli.py`. Use that package until the separate CLI passes MLP, CNN and Transformer smoke tests.

MIT licensed.
