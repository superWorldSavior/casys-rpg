from flask import Flask
import os
from pathlib import Path
from replit import db

def read_markdown_files():
    content_dir = Path('content')
    chapters = []
    
    # Read each markdown file
    for chapter_file in sorted(content_dir.glob('*.md')):
        with open(chapter_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
            # Split content by headers using markdown syntax
            sections = md_content.split('\n## ')
            
            # Process first section (if it exists)
            if sections[0].startswith('# '):
                first_content = sections[0].split('\n', 1)[1] if '\n' in sections[0] else ''
                if first_content.strip():
                    chapters.append(first_content.strip())
            
            # Process remaining sections
            for section in sections[1:]:
                if section.strip():
                    # Reconstruct the section with its header
                    clean_section = f'## {section.strip()}'
                    chapters.append(clean_section)
    
    return chapters

def migrate_to_replit_db():
    chapters = read_markdown_files()
    
    # Clear existing content in DB
    keys = db.prefix("")
    for key in keys:
        if key.startswith('chapter_'):
            del db[key]
    
    # Store new content
    for idx, content in enumerate(chapters):
        key = f'chapter_{idx:03d}'
        db[key] = content
        print(f"Migrated {key}")

if __name__ == "__main__":
    migrate_to_replit_db()
