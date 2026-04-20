#!/bin/bash
# Script d'installation automatique CAMWATER sur PythonAnywhere.
# Usage : à coller/exécuter dans une console Bash PythonAnywhere.
# Tout est idempotent — peut être relancé sans risque.

set -e
echo "╔═══════════════════════════════════════════╗"
echo "║  CAMWATER — Installation PythonAnywhere   ║"
echo "╚═══════════════════════════════════════════╝"

cd "$HOME"

# 1) Cloner le dépôt (ou mettre à jour s'il existe déjà)
if [ -d "$HOME/camwater-app/.git" ]; then
    echo "▶ Dépôt déjà cloné — git pull…"
    cd "$HOME/camwater-app"
    git pull
else
    echo "▶ Clonage du dépôt GitHub…"
    cd "$HOME"
    git clone https://github.com/anthonyambf-amb/camwater-app.git
    cd "$HOME/camwater-app"
fi

# 2) Créer le dossier de données persistantes (hors du repo git)
mkdir -p "$HOME/camwater-data/objectifs"
echo "▶ Dossier données : $HOME/camwater-data"

# 3) Créer le virtualenv Python 3.11 s'il n'existe pas
if [ ! -d "$HOME/camwater-venv" ]; then
    echo "▶ Création du virtualenv Python 3.11…"
    python3.11 -m venv "$HOME/camwater-venv"
fi

# 4) Installer les dépendances
echo "▶ Installation des dépendances Python…"
source "$HOME/camwater-venv/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "$HOME/camwater-app/requirements.txt"

# 5) Préparer le fichier WSGI personnalisé avec le vrai username
WSGI_TEMPLATE="$HOME/camwater-app/pythonanywhere_wsgi.py"
WSGI_OUTPUT="$HOME/camwater-app/wsgi_ready.py"
sed "s|<USERNAME>|$USER|g" "$WSGI_TEMPLATE" > "$WSGI_OUTPUT"
echo "▶ Fichier WSGI prêt : $WSGI_OUTPUT"

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║ INSTALLATION TERMINÉE                                          ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║ PROCHAINES ÉTAPES (onglet 'Web' sur PythonAnywhere) :         ║"
echo "║  1. Add a new web app → Manual configuration → Python 3.11    ║"
echo "║  2. Source code      : /home/$USER/camwater-app"
echo "║  3. Virtualenv       : /home/$USER/camwater-venv"
echo "║  4. WSGI file → coller le contenu de :"
echo "║     cat $HOME/camwater-app/wsgi_ready.py | pbcopy   (macOS)    ║"
echo "║     OU : ouvrir $HOME/camwater-app/wsgi_ready.py"
echo "║  5. Static files :                                             ║"
echo "║     URL /static/   →   /home/$USER/camwater-app/static"
echo "║  6. Cliquer le bouton vert 'Reload'                            ║"
echo "║  7. Visiter : https://$USER.pythonanywhere.com"
echo "╚═══════════════════════════════════════════════════════════════╝"
