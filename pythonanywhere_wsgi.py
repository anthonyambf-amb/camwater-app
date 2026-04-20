"""
WSGI configuration for PythonAnywhere deployment of CAMWATER.

INSTRUCTIONS :
  1. Sur PythonAnywhere → onglet "Web" → section "Code" → clic sur le lien
     WSGI configuration file (ex. /var/www/<username>_pythonanywhere_com_wsgi.py).
  2. Effacer tout le contenu par défaut.
  3. Copier-coller CE fichier intégralement.
  4. Remplacer <USERNAME> (3 occurrences) par votre pseudo PythonAnywhere
     (celui choisi à l'inscription, en lowercase, sans tirets).
  5. Sauvegarder → retour onglet "Web" → clic bouton vert "Reload".
"""
import os
import sys
import secrets

# ─── 1. Ajouter le dossier du projet au sys.path ───────────────────────
# Remplacez <USERNAME> par votre pseudo PythonAnywhere
project_home = '/home/<USERNAME>/camwater-app'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ─── 2. Variables d'environnement de l'application ─────────────────────
# Mode production (pas de page debug exposée)
os.environ['CAMWATER_DEBUG'] = '0'

# Dossier où la base SQLite + les objectifs Excel sont stockés.
# IMPORTANT : hors du dépôt git → ne sera JAMAIS effacé par git pull.
os.environ['CAMWATER_DATA_DIR'] = '/home/<USERNAME>/camwater-data'

# Clé secrète Flask : persistée dans un fichier sur le disque utilisateur
# (conserve les sessions entre reloads). Générée aléatoirement au 1er démarrage.
SECRET_FILE = '/home/<USERNAME>/camwater-data/.secret_key'
try:
    with open(SECRET_FILE, 'r') as f:
        os.environ['CAMWATER_SECRET_KEY'] = f.read().strip()
except FileNotFoundError:
    os.makedirs(os.path.dirname(SECRET_FILE), exist_ok=True)
    new_key = secrets.token_urlsafe(48)
    with open(SECRET_FILE, 'w') as f:
        f.write(new_key)
    os.chmod(SECRET_FILE, 0o600)
    os.environ['CAMWATER_SECRET_KEY'] = new_key

# ─── 3. Importer l'application Flask ────────────────────────────────────
# PythonAnywhere attend une variable nommée `application`
from app import app as application  # noqa: E402
