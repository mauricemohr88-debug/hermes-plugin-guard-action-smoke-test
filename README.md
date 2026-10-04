# Hermes Plugin Guard action smoke test

This repository is a synthetic external-consumer test harness for
[Hermes Plugin Guard](https://github.com/mauricemohr88-debug/hermes-plugin-guard).
It is not another product, a plugin to install, or a claim that static scans prove safety.

The `main` branch consumes the immutable v0.2.1 action commit. The `candidate-cache-fix`
branch consumes a candidate copied from that commit with its broken pip caching removed.
Both use standard GitHub-hosted Ubuntu, macOS and Windows runners. The workflow tests
a clean fixture, expected critical findings,
report-only mode, an invalid target, JSON and SARIF reports, and no target-code execution.
The fixtures are copied from the upstream MIT-licensed regression tests. Do not import
or execute the risky fixture; its source is intentionally unsafe-looking scanner input.

There is deliberately no root `pyproject.toml` or requirements file: this catches
composite actions that incorrectly rely on their consumer's dependency file for caching.
The expected negative steps use `continue-on-error`; explicit assertions decide whether
their failures are correct. A green job means the synthetic acceptance checks passed,
not that every real plugin or self-hosted runner is supported.
