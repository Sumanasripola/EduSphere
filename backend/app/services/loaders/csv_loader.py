import csv

ROWS_PER_CHUNK = 15


def load_csv(file_path: str):
    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return []

    headers = rows[0]
    data_rows = rows[1:]
    chunks = []

    for start in range(0, len(data_rows), ROWS_PER_CHUNK):
        group = data_rows[start:start + ROWS_PER_CHUNK]
        lines = []
        for offset, row in enumerate(group):
            row_num = start + offset + 2
            pairs = [
                f"{headers[i]}={row[i]}"
                for i in range(min(len(headers), len(row)))
                if row[i] != ""
            ]
            if pairs:
                lines.append(f"Row {row_num}: " + ", ".join(pairs))

        if lines:
            chunks.append({
                "text": "\n".join(lines),
                "location": f"rows {start + 2}-{start + 1 + len(group)}",
            })

    return chunks
