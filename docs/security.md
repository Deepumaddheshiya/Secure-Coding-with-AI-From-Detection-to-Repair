# Security Model

## Threat Model

The platform processes potentially malicious source code and therefore follows strict safety boundaries.

## Controls

- temporary sandbox copies for code execution
- size limits for uploaded sources
- no direct shell execution with user-controlled strings
- subprocess calls use argument arrays rather than shell=True
- local-only execution of scanners and compile checks
- temporary workspace cleanup

## Verification Rules

A repair is not considered safe merely because an LLM produced new code. It is only marked as verified after compiler verification and security re-scan evidence align.

## Limitations

This platform is designed for offline research and security assessment workflows. It is not a production-grade remote sandbox and should be used only in local, controlled environments.
