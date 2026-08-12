import pandas as pd
import uuid
import os

OUTPUT_DIR = "generated_excels"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_excel(data, columns):

    import pandas as pd
    import uuid
    import os

    OUTPUT_DIR = "generated_excels"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not data or not columns:
        return None

    # 🔥 Safety fix
    max_len = len(columns)

    clean_data = []
    for row in data:
        if len(row) < max_len:
            row += [""] * (max_len - len(row))
        if len(row) > max_len:
            row = row[:max_len]
        clean_data.append(row)

    df = pd.DataFrame(clean_data, columns=columns)

    file_name = f"{uuid.uuid4()}.xlsx"
    file_path = os.path.join(OUTPUT_DIR, file_name)

    df.to_excel(file_path, index=False)

    return file_path