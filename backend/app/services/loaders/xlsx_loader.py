"""
Loads a .xlsx file into normalized {"text", "location"} chunks.

Spreadsheets need different handling than prose: dumping raw cells as text
loses all meaning ("4200" means nothing on its own). Instead, each chunk
is a small group of rows with the column headers attached to every row,
so a chunk reads like "Row 14: Product=Widget, Revenue=4200" — something
the embedding model and the LLM can actually reason about.
"""
import openpyxl

ROWS_PER_CHUNK = 15


def load_xlsx(file_path: str):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    chunks = []

    for sheet in wb.worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue

        headers = [str(h) if h is not None else f"col{i}" for i, h in enumerate(rows[0])]
        data_rows = rows[1:]

        if not data_rows:
            continue

        for start in range(0, len(data_rows), ROWS_PER_CHUNK):
            group = data_rows[start:start + ROWS_PER_CHUNK]
            lines = []
            for offset, row in enumerate(group):
                row_num = start + offset + 2  # +2: header is row 1, data is 1-indexed
                pairs = [
                    f"{headers[i]}={row[i]}"
                    for i in range(len(headers))
                    if i < len(row) and row[i] is not None
                ]
                if pairs:
                    lines.append(f"Row {row_num}: " + ", ".join(pairs))

            if lines:
                chunks.append({
                    "text": "\n".join(lines),
                    "location": f"{sheet.title}, rows {start + 2}-{start + 1 + len(group)}",
                })

    return chunks
