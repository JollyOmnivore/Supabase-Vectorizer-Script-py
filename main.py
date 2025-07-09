import os
import openai
import PyPDF2
from supabase import create_client, Client
import json
from dotenv import load_dotenv
import docx
import pandas as pd
from pptx import Presentation

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TABLE_NAME = "documents"

if not SUPABASE_URL or not SUPABASE_KEY or not OPENAI_API_KEY:
    raise ValueError("Missing SUPABASE_URL, SUPABASE_KEY, or OPENAI_API_KEY in environment variables.")

openai.api_key = OPENAI_API_KEY

CHUNK_SIZE = 800

# --- SUPABASE CLIENT ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def extract_text_from_pdf(pdf_path):
    text = os.path.basename(pdf_path) + "\n"
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        return os.path.basename(txt_path) + "\n" + f.read()

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = os.path.basename(docx_path) + "\n"
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_csv(csv_path):
    import pandas as pd
    df = pd.read_csv(csv_path)
    text = os.path.basename(csv_path) + "\n"
    for row in df.itertuples(index=False):
        row_text = "\t".join([str(cell) for cell in row if pd.notnull(cell)])
        if row_text.strip():
            text += row_text + "\n"
    return text

def extract_text_from_xlsx(xlsx_path):
    import pandas as pd
    df_dict = pd.read_excel(xlsx_path, sheet_name=None)
    text = os.path.basename(xlsx_path) + "\n"
    for sheet_name, df in df_dict.items():
        text += f"--- Sheet: {sheet_name} ---\n"
        for row in df.itertuples(index=False):
            row_text = "\t".join([str(cell) for cell in row if pd.notnull(cell)])
            if row_text.strip():
                text += row_text + "\n"
    return text

def extract_text_from_pptx(pptx_path):
    prs = Presentation(pptx_path)
    text = os.path.basename(pptx_path) + "\n"
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    return text

def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext == ".txt":
        return extract_text_from_txt(filepath)
    elif ext == ".docx":
        return extract_text_from_docx(filepath)
    elif ext == ".csv":
        return extract_text_from_csv(filepath)
    elif ext == ".xlsx":
        return extract_text_from_xlsx(filepath)
    elif ext == ".pptx":
        return extract_text_from_pptx(filepath)
    else:
        print(f"Skipping unsupported file type: {filepath}")
        return None

def chunk_text(text, chunk_size=CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size) if text[i:i+chunk_size].strip()]

def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def upload_to_supabase(content, embedding, metadata=None):
    data = {
        "content": content,
        "embedding": embedding,
        "metadata": metadata or {}
    }
    supabase.table(TABLE_NAME).insert(data).execute()

def main():
    filedump_dir = "filedump"
    for filename in os.listdir(filedump_dir):
        filepath = os.path.join(filedump_dir, filename)
        if not os.path.isfile(filepath):
            continue
        text = extract_text_from_file(filepath)
        if not text:
            continue
        try:
            chunks = chunk_text(text)
            for idx, chunk in enumerate(chunks):
                print(f"Embedding and uploading chunk {idx+1}/{len(chunks)} from {filename}")
                emb = get_embedding(chunk)
                metadata = {"chunk_index": idx, "source_file": filename}
                upload_to_supabase(chunk, emb, metadata)
            print(f"Finished processing {filename}, deleting file.")
            os.remove(filepath)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    print("All files in filedump processed, uploaded, and deleted.")

if __name__ == "__main__":
    main()
