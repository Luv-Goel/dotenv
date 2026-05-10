# Dotenv ðŸ“‹

<div align="center">

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-lightgrey)]()

**.env file toolkit â€” load, validate, merge, diff, template, and sort. Zero dependencies.**

</div>

---

## Features

- **Load & parse** â€” Read `.env` files with proper quoting, variable expansion, and multiline support
- **Validation** â€” Check for missing vars, invalid keys, syntax errors, and reference cycles
- **Merge** â€” Combine multiple `.env` files with conflict resolution
- **Diff** â€” Compare `.env` files and show added/removed/changed entries
- **Templating** â€” Render `.env` as template with `{{VAR}}` substitution
- **Sort** â€” Alphabetize keys for clean, consistent files
- **Validate against schema** â€” Check `.env` against a reference `.env.example`
- **Zero dependencies** â€” Pure Python 3.8+, no pip packages required

## Quick Start

```bash
pip install dotenv-toolkit

# Load and display a .env file
dotenv load .env

# Validate against schema
dotenv check .env --against .env.example

# Merge files
dotenv merge .env .env.local .env.prod --output .env.merged

# Diff two files
dotenv diff .env.staging .env.production

# Template substitution
dotenv template .env.tpl --output .env

# Sort keys alphabetically
dotenv sort .env --output .env.sorted
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `dotenv load [file]` | Parse and display .env file contents |
| `dotenv check [file]` | Validate .env file (syntax, vars, schema) |
| `dotenv merge [files...]` | Merge multiple .env files |
| `dotenv diff [a] [b]` | Show difference between two .env files |
| `dotenv template [file]` | Substitute `{{VAR}}` templates with values |
| `dotenv sort [file]` | Sort environment variable keys |

## Architecture

```
dotenv/
â”œâ”€â”€ dotenv/
â”‚   â”œâ”€â”€ __init__.py    # Exports and version
â”‚   â”œâ”€â”€ cli.py         # CLI entry point
â”‚   â””â”€â”€ core.py        # Parsing, validation, merge, diff, template
â”œâ”€â”€ pyproject.toml
â””â”€â”€ README.md
```

## License

MIT â€” see [LICENSE](LICENSE).
