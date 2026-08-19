# RepoDoctor

RepoDoctor is a command-line repository health analyzer for Python projects.

It scans a repository for common code-quality, security, structure, and Git problems and produces a health score with actionable recommendations.

## Features

- Python AST analysis
- Function complexity detection
- Large-function detection
- Deep-nesting detection
- Excessive-argument detection
- TODO/FIXME detection
- Basic hardcoded-secret detection
- Git repository health analysis
- README and `.gitignore` checks
- Health score from 0–100
- Actionable recommendations
- JSON output
- CI-friendly score thresholds

## Installation

Clone the repository and install it:

```bash
git clone <your-repository-url>
cd RepoDoctor

python -m venv .venv
source .venv/bin/activate

pip install -e .
