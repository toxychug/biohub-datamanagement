# 🔧 Scripts

One-time utility scripts for development and project generation.

## Files

- **generate_gap_analysis.py** — Generate gap analysis report
- **generate_guide.py** — Generate project guide
- **generate_report.py** — Generate project report
- **test_post_endpoint.sh** — Test single POST endpoint (see ../test_all_endpoints.sh for main tests)

## Usage

These scripts are for development and one-time setup. They're not part of the core application.

```bash
python scripts/generate_report.py
./scripts/test_post_endpoint.sh
```

For regular testing, use:
```bash
pytest
# or
./test_all_endpoints.sh
```
