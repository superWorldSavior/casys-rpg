from replit import db
from replit.object_storage import Client
import os
import json

def migrate_to_storage():
    print("Starting migration to Object Storage...")
    
    # Initialize Object Storage
    client = Client()
    BUCKET_ID = os.environ.get('REPLIT_BUCKET_ID', 'replit-objstore-f05f56c7-9da7-4fbe-8b1f-ec80f5185697')
    
    try:
        # Get all chapter keys from DB
        chapter_keys = [k for k in db.prefix("") if k.startswith('chapter_')]
        chapter_keys.sort()
        
        if not chapter_keys:
            print("No chapters found in database to migrate.")
            return
        
        print(f"Found {len(chapter_keys)} chapters to migrate.")
        
        # Migrate each chapter to Object Storage
        for key in chapter_keys:
            content = db[key]
            client.upload_from_text(
                BUCKET_ID,
                key,
                json.dumps(content),
                metadata={'index': key.split('_')[1]}
            )
            print(f"Migrated {key}")
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate_to_storage()
