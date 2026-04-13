# csv-diff-reporter

> CLI tool that compares two CSV files and generates a human-readable diff report with change summaries.

---

## Installation

```bash
pip install csv-diff-reporter
```

Or install from source:

```bash
git clone https://github.com/yourusername/csv-diff-reporter.git
cd csv-diff-reporter
pip install .
```

---

## Usage

```bash
csv-diff-reporter old.csv new.csv
```

**With options:**

```bash
csv-diff-reporter old.csv new.csv --key id --output report.txt --format markdown
```

**Options:**

| Flag | Description |
|------|-------------|
| `--key` | Column to use as the unique row identifier (default: first column) |
| `--output` | Write report to a file instead of stdout |
| `--format` | Output format: `text`, `markdown`, or `html` (default: `text`) |

**Example output:**

```
Summary: 3 added, 1 removed, 5 modified

[ADDED]    row id=42  name="Alice"  age=30
[REMOVED]  row id=17  name="Bob"    age=25
[MODIFIED] row id=9   age: 28 → 29
```

---

## Requirements

- Python 3.8+

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

This project is licensed under the [MIT License](LICENSE).