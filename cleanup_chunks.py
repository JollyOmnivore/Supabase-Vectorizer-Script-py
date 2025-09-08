import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "nationwide_quote_documents"

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def delete_chunks_by_file_title(file_title):
    try:
        # Get all IDs to delete
        all_chunks = supabase.table(TABLE_NAME).select("id").eq("metadata->>file_title", file_title).execute()
        chunk_ids = [chunk['id'] for chunk in all_chunks.data]
        
        print(f"Found {len(chunk_ids)} chunks with file_title: '{file_title}'")
        
        if len(chunk_ids) == 0:
            print("No chunks found to delete.")
            return
        
        confirm = input(f"Are you sure you want to delete {len(chunk_ids)} chunks? (y/N): ")
        if confirm.lower() != 'y':
            print("Deletion cancelled.")
            return
        
        # Delete in batches of 100
        batch_size = 100
        deleted_count = 0
        
        for i in range(0, len(chunk_ids), batch_size):
            batch_ids = chunk_ids[i:i + batch_size]
            
            try:
                result = supabase.table(TABLE_NAME).delete().in_("id", batch_ids).execute()
                deleted_count += len(batch_ids)
                print(f"Deleted batch {i//batch_size + 1}: {deleted_count}/{len(chunk_ids)} chunks")
            except Exception as batch_error:
                print(f"Error deleting batch {i//batch_size + 1}: {batch_error}")
                continue
        
        print(f"Successfully deleted {deleted_count} chunks for file: '{file_title}'")
        
    except Exception as e:
        print(f"Error deleting chunks: {e}")

if __name__ == "__main__":
    file_title = "1 in 1M Data All Names.xlsx"
    delete_chunks_by_file_title(file_title)
