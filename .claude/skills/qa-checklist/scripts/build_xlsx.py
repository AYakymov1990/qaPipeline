#!/usr/bin/env python3
"""Генерує 03-checklist.xlsx з 03-checklist.md (формат — templates/03-checklist.md).

Використання:
    python3 build_xlsx.py work/<ID>/03-checklist.md [-o work/<ID>/03-checklist.xlsx]

Потрібен openpyxl: pip install openpyxl
"""
import argparse
import math
import re
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

REQUIRED = ["№", "Розділ", "Блок", "Перевірка", "Очікуваний результат", "Пріоритет", "Вимога"]
PRIORITIES = ["Критичний", "Високий", "Середній", "Низький"]
RESULTS = ["Pass", "Fail", "Blocked", "Skip"]
REGRESSION_SECTION = "Регресійні перевірки"
REGRESSION_PREFIX = "[Регресія]"

# колонки xlsx: (заголовок, ширина)
COLUMNS = [("№", 7), ("Перевірка", 55), ("Очікуваний результат", 55),
           ("Пріоритет", 13), ("Вимога", 18), ("Результат", 14)]

PRIORITY_FILL = {"Критичний": "FF9999", "Високий": "FFCC99", "Середній": "FFF2CC", "Низький": "E2EFDA"}
RESULT_FILL = {"Pass": "C6EFCE", "Fail": "FFC7CE", "Blocked": "FFEB9C", "Skip": "D9D9D9"}

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP_TOP = Alignment(wrap_text=True, vertical="top")
SECTION_FILL = PatternFill("solid", fgColor="1F3864")
BLOCK_FILL = PatternFill("solid", fgColor="D9E1F2")
HEADER_FILL = PatternFill("solid", fgColor="BFBFBF")


def clean(text):
    """Прибирає markdown-розмітку (`код`, **жирний**) для Excel."""
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text.replace("`", "")).strip()


def split_row(line):
    line = line.strip().strip("|")
    cells = re.split(r"(?<!\\)\|", line)
    return [clean(c.replace("\\|", "|")) for c in cells]


def section(text, heading):
    """Текст між '## heading' і наступним '## '."""
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def parse(md):
    title_m = re.search(r"^# (.+)$", md, re.M)
    title = title_m.group(1).strip() if title_m else "Чек-лист"

    desc = []
    for line in section(md, "Опис").splitlines():
        m = re.match(r"^\s*-\s+\*\*(.+?):\*\*\s*(.*)$", line)
        if m:
            desc.append((clean(m.group(1)), clean(m.group(2))))

    table = [l for l in section(md, "Перевірки").splitlines() if l.strip().startswith("|")]
    if len(table) < 2:
        sys.exit("Не знайдено таблицю в розділі «## Перевірки».")
    header = split_row(table[0])
    missing = [c for c in REQUIRED if c not in header]
    if missing:
        sys.exit(f"У таблиці бракує колонок: {', '.join(missing)}")
    rows = []
    for line in table[2:]:
        cells = split_row(line)
        if not any(cells):
            continue
        cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells)))
    return title, desc, rows


def check(rows):
    warnings = []
    for i, r in enumerate(rows, 1):
        if r["№"] != str(i):
            warnings.append(f"рядок {i}: № = «{r['№']}», очікувалось {i} (нумерація наскрізна)")
        if r["Пріоритет"] not in PRIORITIES:
            warnings.append(f"№ {r['№']}: пріоритет «{r['Пріоритет']}» не з переліку {PRIORITIES}")
        if r.get("Результат") and r["Результат"] not in RESULTS:
            warnings.append(f"№ {r['№']}: результат «{r['Результат']}» не з переліку {RESULTS}")
        if not r["Перевірка"] or not r["Очікуваний результат"]:
            warnings.append(f"№ {r['№']}: порожня перевірка або очікуваний результат")
        is_reg = r["Розділ"] == REGRESSION_SECTION
        if is_reg != r["Перевірка"].startswith(REGRESSION_PREFIX):
            warnings.append(f"№ {r['№']}: мітка «{REGRESSION_PREFIX}» тільки й обовʼязково в розділі «{REGRESSION_SECTION}»")
    return warnings


def row_height(values):
    lines = 1
    for (_, width), value in zip(COLUMNS, values):
        text = str(value or "")
        chars = max(int(width * 1.1), 1)
        lines = max(lines, sum(max(1, math.ceil(len(p) / chars)) for p in text.split("\n")))
    return max(15, 15 * lines)


def build(title, desc, rows, out):
    wb = Workbook()
    ws = wb.active
    ws.title = "Чек-лист"
    ncol = len(COLUMNS)
    for i, (_, width) in enumerate(COLUMNS, 1):
        ws.column_dimensions[chr(64 + i)].width = width

    r = 1
    ws.cell(r, 1, title).font = Font(bold=True, size=14)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
    r += 2
    for key, value in desc:
        ws.cell(r, 1, key).font = Font(bold=True)
        ws.cell(r, 1).alignment = WRAP_TOP
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.cell(r, 3, value).alignment = WRAP_TOP
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=ncol)
        ws.row_dimensions[r].height = max(15, 15 * math.ceil(len(value) / 100))
        r += 1
    r += 1

    for i, (name, _) in enumerate(COLUMNS, 1):
        c = ws.cell(r, i, name)
        c.font, c.fill, c.border, c.alignment = Font(bold=True), HEADER_FILL, BORDER, WRAP_TOP
    r += 1

    first_data = r
    dv = DataValidation(type="list", formula1='"' + ",".join(RESULTS) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    prev_section = prev_block = None
    for row in rows:
        if row["Розділ"] != prev_section:
            c = ws.cell(r, 1, row["Розділ"])
            c.font, c.fill, c.alignment = Font(bold=True, color="FFFFFF"), SECTION_FILL, WRAP_TOP
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
            r += 1
            prev_section, prev_block = row["Розділ"], None
        if row["Блок"] and row["Блок"] != prev_block:
            c = ws.cell(r, 1, row["Блок"])
            c.font, c.fill, c.alignment = Font(bold=True), BLOCK_FILL, WRAP_TOP
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
            r += 1
            prev_block = row["Блок"]
        values = [int(row["№"]) if row["№"].isdigit() else row["№"], row["Перевірка"],
                  row["Очікуваний результат"], row["Пріоритет"], row["Вимога"], row.get("Результат", "")]
        for i, v in enumerate(values, 1):
            c = ws.cell(r, i, v)
            c.border, c.alignment = BORDER, WRAP_TOP
        dv.add(ws.cell(r, ncol))
        ws.row_dimensions[r].height = row_height(values)
        r += 1
    last = r - 1

    pr = f"D{first_data}:D{last}"
    for value, color in PRIORITY_FILL.items():
        ws.conditional_formatting.add(pr, CellIsRule(operator="equal", formula=[f'"{value}"'],
                                                     fill=PatternFill("solid", bgColor=color)))
    rr = f"F{first_data}:F{last}"
    for value, color in RESULT_FILL.items():
        ws.conditional_formatting.add(rr, CellIsRule(operator="equal", formula=[f'"{value}"'],
                                                     fill=PatternFill("solid", bgColor=color)))

    ws.freeze_panes = None  # без закріпленої шапки — правило qa-checklist
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("md", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    args = ap.parse_args()
    out = args.out or args.md.with_suffix(".xlsx")
    title, desc, rows = parse(args.md.read_text(encoding="utf-8"))
    warnings = check(rows)
    build(title, desc, rows, out)
    print(f"Готово: {out} — перевірок: {len(rows)}")
    for w in warnings:
        print(f"УВАГА: {w}")
    sys.exit(1 if warnings else 0)


if __name__ == "__main__":
    main()
