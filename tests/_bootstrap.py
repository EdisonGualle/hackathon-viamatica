import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from ingestion.load_data import run_pipeline


_PIPELINE_CACHE = None


def ensure_pipeline():
    global _PIPELINE_CACHE
    if _PIPELINE_CACHE is None:
        _PIPELINE_CACHE = run_pipeline()
    return _PIPELINE_CACHE
