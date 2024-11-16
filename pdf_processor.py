import os
import re
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
import json
from concurrent.futures import ThreadPoolExecutor
import pathlib

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def find_pdf_in_project():
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.pdf'):
                return os.path.join(root, file)
    return None

def get_pdf_folder_name(pdf_path):
    """Generate folder name from PDF filename without extension."""
    base_name = os.path.basename(pdf_path)
    folder_name = os.path.splitext(base_name)[0]
    # Clean folder name to ensure it's valid
    folder_name = re.sub(r'[^\w\s-]', '_', folder_name)
    return folder_name

def extraire_sections(pdf_path, base_output_dir="sections"):
    """
    Extrait les sections d'un PDF en Markdown et les stocke dans un dossier nommé d'après le PDF.
    
    Args:
        pdf_path: Chemin d'accès au fichier PDF.
        base_output_dir: Répertoire de base pour tous les PDFs traités.
    """
    # Create base output directory if it doesn't exist
    os.makedirs(base_output_dir, exist_ok=True)
    
    # Create PDF-specific folder
    pdf_folder_name = get_pdf_folder_name(pdf_path)
    output_dir = os.path.join(base_output_dir, pdf_folder_name)
    os.makedirs(output_dir, exist_ok=True)
    
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    section_texte = ""
    section_num = None
    section_metadata = []
    
    def process_section(file_path):
        analyser_texte(file_path)

    with ThreadPoolExecutor() as executor:
        for page_num in range(num_pages):
            try:
                page = reader.pages[page_num]
                texte = page.extract_text()

                if texte:
                    lignes = texte.splitlines()
                    for ligne in lignes:
                        ligne = ligne.strip()
                        if ligne.isdigit():
                            if section_num is not None:
                                # Save previous section
                                file_path = os.path.join(output_dir, f"{section_num}.md")
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(f"# Section {section_num}\n\n")
                                    f.write(section_texte.strip())
                                executor.submit(process_section, file_path)
                                
                                section_metadata.append({
                                    'section_number': section_num,
                                    'file_path': os.path.relpath(file_path, base_output_dir),
                                    'pdf_name': pdf_folder_name
                                })
                            
                            section_num = int(ligne)
                            section_texte = f"# Section {section_num}\n\n"
                        else:
                            if section_num is not None:
                                section_texte += ligne + "\n"

            except Exception as e:
                print(f"Erreur lors du traitement de la page {page_num + 1}: {e}")

        # Save last section
        if section_num is not None:
            file_path = os.path.join(output_dir, f"{section_num}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# Section {section_num}\n\n")
                f.write(section_texte.strip())
            executor.submit(process_section, file_path)
            
            section_metadata.append({
                'section_number': section_num,
                'file_path': os.path.relpath(file_path, base_output_dir),
                'pdf_name': pdf_folder_name
            })

    # Save metadata in the PDF-specific folder
    metadata_path = os.path.join(output_dir, 'section_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(section_metadata, f, ensure_ascii=False, indent=4)
    print(f'Métadonnées sauvegardées dans: {metadata_path}')
    
    return output_dir

def analyser_texte(file_path):
    """Utilise une IA pour analyser le texte et ajuster le formatage des numéros de chapitre."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            contenu = f.read()

        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that formats text for gamebooks."},
                {"role": "user", "content": f"Here is a text extracted from a gamebook:\n\n{contenu}\n\nIdentify numbers representing chapters that the reader should go to and surround them with [[ ]]. Leave other numbers as they are. Don't Say : Certainly! Here's the formatted text: Or Something else than the text"}
            ]
        )

        texte_modifie = completion.choices[0].message.content

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(texte_modifie)

    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier {file_path}: {e}")

if __name__ == "__main__":
    pdf_path = find_pdf_in_project()
    if pdf_path:
        print(f'PDF trouvé: {pdf_path}')
        output_dir = extraire_sections(pdf_path)
        print(f'Sections extraites dans: {output_dir}')
    else:
        print('Aucun PDF trouvé dans le projet')
