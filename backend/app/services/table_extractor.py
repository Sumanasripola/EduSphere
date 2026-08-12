import camelot

def extract_tables(pdf_path):

    tables = camelot.read_pdf(pdf_path)
    

    table_text = []

    for table in tables:

        table_text.append(table.df.to_string())

    return table_text