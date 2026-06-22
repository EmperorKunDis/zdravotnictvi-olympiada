"""
Vercel serverless ASGI entrypoint.

Vercel runtime detects the module-level ``app`` (an ASGI application) and wraps
it automatically — no uvicorn needed. We only re-export the lightweight FastAPI
app defined in the repo-root ``app.py`` (rule-based mode, no heavy deps).
"""

import sys
from pathlib import Path

# Make the repo root importable so ``app.py`` (and its relative data/frontend
# paths, which it resolves from its own __file__) work inside the lambda.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402,F401  (re-exported for the Vercel Python runtime)
