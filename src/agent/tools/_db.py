from __future__ import annotations

import os
import sqlite3
from typing import Any

import pandas as pd

DB_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'fraudia.db'))


def query_df(sql: str, params: tuple[Any, ...] = ()) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(sql, conn, params=params)
