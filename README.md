# Supabase Vector Embedding Uploader

This project processes a folder of documents, generates OpenAI embeddings for their content, and uploads the results to a Supabase vector store table. It is designed for bulk ingestion of various document types into a vector database for semantic search, retrieval-augmented generation, or other AI-powered workflows.

## Features
- **Supported file types:**
  - PDF (`.pdf`)
  - Text (`.txt`)
  - Word (`.docx`)
  - Excel (`.xlsx`)
  - CSV (`.csv`)
  - PowerPoint (`.pptx`)
- Automatically chunks large documents for embedding
- Prepends the filename to the content for traceability
- Uploads each chunk as a row to Supabase with content, embedding, and metadata
- Deletes each file after successful upload

## Setup

### 1. Clone the repository

```
git clone <your-repo-url>
cd <your-repo-directory>
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install these packages:

```
pip install openai PyPDF2 python-docx pandas openpyxl python-dotenv python-pptx supabase
```

### 3. Environment Variables

Create a `.env` file in the project root with the following content:

```
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-service-role-or-anon-key
OPENAI_API_KEY=your-openai-api-key
```

- **SUPABASE_URL**: Your Supabase project URL (e.g. `https://xxxx.supabase.co`)
- **SUPABASE_KEY**: Your Supabase service role key or anon key (service role recommended for inserts)
- **OPENAI_API_KEY**: Your OpenAI API key

### 4. Prepare your files

Place all files you want to process in the `filedump` directory (create it if it doesn't exist).

## Usage

Run the script:

```
python main.py
```

- The script will process every supported file in the `filedump` directory.
- For each file, it will extract text, chunk it, generate embeddings, upload to Supabase, and then delete the file.
- Metadata includes the chunk index and source filename for each chunk.

## Supabase Table Schema

Your Supabase table (default: `documents`) should have at least the following columns:

- `id` (uuid or serial, primary key)
- `content` (text)
- `embedding` (vector/float8[]/jsonb, depending on your setup)
- `metadata` (jsonb)

Example (for pgvector):
```sql
create table documents (
  id uuid primary key default gen_random_uuid(),
  content text,
  embedding vector(1536), -- adjust size to your embedding model
  metadata jsonb
);
```

## Customization
- To support more file types, add a new extraction function and update `extract_text_from_file`.
- To change chunk size, modify the `CHUNK_SIZE` variable in `main.py`.
- To change the Supabase table, update the `TABLE_NAME` variable.

## License
MIT 