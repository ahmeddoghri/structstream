# Security Policy

## Supported versions

This project is pre-1.0. Security fixes land on `main`; track the latest commit.

## Reporting a vulnerability

Please do not open a public issue for security problems. Use GitHub's
[private vulnerability reporting](https://github.com/ahmeddoghri/structstream/security/advisories/new)
or email the maintainer. Include a description of the issue and its impact,
steps to reproduce (a minimal proof-of-concept helps), and any suggested fix.

You can expect an acknowledgement within a few days. Once a fix is out you will
be credited unless you would rather stay anonymous.

## Scope notes

structstream is a pure-stdlib library with no runtime dependencies. It parses
text with `json.loads` after a conservative repair pass, so it does not evaluate
code and there is no `eval` anywhere near it. The repair is regex-based and
bounded, but as always, treat model output as untrusted input and validate the
repaired value against your schema before you act on it. That is exactly what
the schema validator is for.
