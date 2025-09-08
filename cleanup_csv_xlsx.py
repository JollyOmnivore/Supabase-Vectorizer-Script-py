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

def delete_chunks_by_file_types(file_extensions):
    try:
        all_chunk_ids = []
        
        for ext in file_extensions:
            print(f"Finding chunks with file_type: {ext}")
            chunks = supabase.table(TABLE_NAME).select("id").eq("metadata->>file_type", ext).execute()
            chunk_ids = [chunk['id'] for chunk in chunks.data]
            all_chunk_ids.extend(chunk_ids)
            print(f"Found {len(chunk_ids)} chunks with file_type: {ext}")
        
        print(f"\nTotal chunks to delete: {len(all_chunk_ids)}")
        
        if len(all_chunk_ids) == 0:
            print("No chunks found to delete.")
            return
        
        confirm = input(f"Are you sure you want to delete {len(all_chunk_ids)} chunks from CSV and XLSX files? (y/N): ")
        if confirm.lower() != 'y':
            print("Deletion cancelled.")
            return
        
        # Delete in batches of 100
        batch_size = 100
        deleted_count = 0
        
        for i in range(0, len(all_chunk_ids), batch_size):
            batch_ids = all_chunk_ids[i:i + batch_size]
            
            try:
                result = supabase.table(TABLE_NAME).delete().in_("id", batch_ids).execute()
                deleted_count += len(batch_ids)
                print(f"Deleted batch {i//batch_size + 1}: {deleted_count}/{len(all_chunk_ids)} chunks")
            except Exception as batch_error:
                print(f"Error deleting batch {i//batch_size + 1}: {batch_error}")
                continue
        
        print(f"Successfully deleted {deleted_count} chunks from CSV and XLSX files")
        
    except Exception as e:
        print(f"Error deleting chunks: {e}")

def show_file_type_summary():
    try:
        print("Current file types in database:")
        result = supabase.table(TABLE_NAME).select("metadata->>file_type", count="exact").execute()
        
        file_types = {}
        for row in result.data:
            file_type = row.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        for file_type, count in sorted(file_types.items()):
            print(f"  {file_type}: {count} chunks")
        
        return file_types
        
    except Exception as e:
        print(f"Error getting file type summary: {e}")
        return {}

if __name__ == "__main__":
    print("=== File Type Summary (Before Cleanup) ===")
    show_file_type_summary()
    
    print("\n=== Starting Cleanup ===")
    file_extensions_to_delete = [".csv", ".xlsx"]
    delete_chunks_by_file_types(file_extensions_to_delete)
    
    print("\n=== File Type Summary (After Cleanup) ===")
    show_file_type_summary()












