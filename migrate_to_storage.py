from replit.object_storage import Client
import os
from pathlib import Path

def migrate_to_storage():
    print("Starting migration to Object Storage...")
    client = Client()
    BUCKET_ID = os.environ.get('REPLIT_BUCKET_ID')
    
    try:
        # Read directly from markdown files
        content_dir = Path('content')
        for file_path in sorted(content_dir.glob('*.md')):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                key = file_path.stem + '.md'  # Keep .md extension
                # Simple direct upload without metadata
                client.upload_from_text(BUCKET_ID, key, content)
                print(f"Migrated {key}")
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate_to_storage()