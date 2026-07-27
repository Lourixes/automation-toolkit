#!/usr/bin/env python3
"""Turn a raw spreadsheet export into a clean summary report.

Reads an .xlsx or .csv, produces a new workbook with the cleaned data plus a
summary sheet (row counts, sums and means of numeric columns, optionally grouped).

Usage:
    python excel_report.py --in export.xlsx --out report.xlsx --group-by "Region"
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

log = logging.getLogger("excel_report")


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError(f"Unsupported input format: {path.suffix}")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [str(c).strip() for c in cleaned.columns]
    cleaned = cleaned.dropna(how="all").drop_duplicates()
    for col in cleaned.select_dtypes(include="object").columns:
        cleaned[col] = cleaned[col].astype(str).str.strip()
    return cleaned


def summarize(df: pd.DataFrame, group_by: str | None) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if group_by:
        if group_by not in df.columns:
            raise ValueError(f"Column {group_by!r} not found. Available: {list(df.columns)}")
        grouped = df.groupby(group_by)
        summary = grouped[numeric_cols].agg(["count", "sum", "mean"]) if numeric_cols else grouped.size().to_frame("count")
        summary.columns = ["_".join(c) if isinstance(c, tuple) else c for c in summary.columns]
        return summary.reset_index()
    totals = {"rows": [len(df)]}
    for col in numeric_cols:
        totals[f"{col}_sum"] = [df[col].sum()]
        totals[f"{col}_mean"] = [round(df[col].mean(), 2)]
    return pd.DataFrame(totals)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="input", required=True, help="Input .xlsx or .csv")
    parser.add_argument("--out", default="report.xlsx", help="Output workbook")
    parser.add_argument("--group-by", default=None, help="Optional column to group the summary by")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    input_path = Path(args.input)
    if not input_path.exists():
        log.error("Input file not found: %s", input_path)
        return 1

    try:
        df = clean(load_table(input_path))
        summary = summarize(df, args.group_by)
    except ValueError as exc:
        log.error("%s", exc)
        return 1

    with pd.ExcelWriter(args.out, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Data", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)

    log.info("Report written to %s (%d rows, summary %dx%d)", args.out, len(df), *summary.shape)
    return 0


if __name__ == "__main__":
    sys.exit(main())
