#!/bin/bash
cd "$(dirname "$0")"
echo "=== CAMWATER - Application Données Commerciales ==="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python 3 non trouvé. Installez Python 3."
    exit 1
fi

# Installer Flask si nécessaire
python3 -c "import flask" 2>/dev/null || {
    echo "Installation de Flask..."
    pip3 install flask
}

# Créer le répertoire data si nécessaire
mkdir -p data

echo "Démarrage du serveur..."
echo "Ouvrez http://localhost:5050 dans votre navigateur"
echo ""
python3 app.py
