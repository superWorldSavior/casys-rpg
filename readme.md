créer venv
vérifier qu'on est dans venv
intaller requirement.txt

cd frontend
npm install

revenir dans root
python app.py

LEXIQUE :
- chapitres : tous les chapitres qui ne sont pas numérotés par des numéros
- pré-section : tous les chapitres qui ne sont pas numérotés
- sections : tous les chapitres numérotés
- metadata : stock les informations des lives, par exemple la section à laquelle appartient une image, le nombre de sections d'un livre, si le livre est prêt ou pas


TIPS :
Il faut effacer les files dans le dossier metadata pour enlever l'affichage dans la gallerie
L'upload ne marche pas si le fochier est déjà là je crois

TODO :
[ ] debug cover imagge
[ ] debug l'extraction des sections ou le supprimer car plus besoin 
[ ] enlever l'enregistrement et la lecture dans le dossier / fichier centralisé metadata, normalement on lisait les metadata depuis le dossier du livre 
[ ] réussir à extract les pré-sections en chapitres complets et les stocker dans des fichiers différents en respectant la mise en forme
[ ] extraire également dès le début la section 1
[ ] extraire les règles et les structurer, prêtes à l'emploi pour le llm
[ ] faire que le chat lise les chapitres dans l'ordre
[ ] faire qu'on puisse rouler les dès via le chat
[ ] faire que le chat comprenne quand il faut rouler les dès et sauvegarde le tirage pour une demande des règles
[ ] faire que l'ia mette en forme les sections n+1 par rapport au déroulement de l'aventure
[ ] faire que les images apparaissent dans le chat quand la section en comporte