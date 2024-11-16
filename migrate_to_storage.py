from replit import db
from replit.object_storage import Client
import os
import json
from datetime import datetime

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
        
        # Migrate each chapter to Object Storage with versioning
        for key in chapter_keys:
            content = db[key]
            timestamp = datetime.utcnow().isoformat()
            
            # Create versioned key for initial version
            versioned_key = f"{key}_v1"
            
            # Upload the content with version metadata
            client.upload_from_text(
                BUCKET_ID,
                versioned_key,
                json.dumps(content),
                metadata={
                    'index': key.split('_')[1],
                    'version': '1',
                    'timestamp': timestamp,
                    'base_key': key
                }
            )
            
            # Store base reference file
            client.upload_from_text(
                BUCKET_ID,
                key,  # base key without version
                json.dumps({'latest_version': 1}),
                metadata={'index': key.split('_')[1]}
            )
            
            print(f"Migrated {key} with initial version")
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate_to_storage()
