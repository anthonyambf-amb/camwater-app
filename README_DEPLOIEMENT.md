# CAMWATER — Déploiement & Accès distant

## Rôles et contrôle d'accès

Trois rôles exclusifs, **trois URL de connexion distinctes** à partager selon le profil :

| Rôle | URL à partager | Identification | Accès |
|------|---------------|----------------|-------|
| `central` | `/central` | Nom + matricule (format `1A23`) | Tout : saisies, consultations, tableau de bord, objectifs, paiements électroniques, exports |
| `agent_terrain` | `/agences` | Matricule + agence + date | **Uniquement** `/recettes-jour/saisie` et `/branchements-jour/saisie` |
| `direction` | `/direction` | **Aucune** (accès direct) | **Lecture seule** : tableau de bord + consultations + exports Excel/PDF |

La page d'accueil `/` présente les 3 entrées pour faciliter l'orientation.

Un hook Flask `@app.before_request` applique le périmètre :
- Agent terrain hors périmètre → redirection `/terrain` (pages) ou `HTTP 403` (API)
- Direction → toute requête non-GET est refusée (403) ; les pages de saisie renvoient vers `/dashboard`

Les données saisies par les agents distants sont écrites dans la même base
SQLite centrale → visibles en temps réel par le central et la direction.

---

## Lancement local

```bash
cd camwater-app
python3 app.py
```

Par défaut l'application écoute sur `0.0.0.0:5050` → accessible à toutes les
machines du même réseau local via `http://<ip-serveur>:5050`.

Variables d'environnement :

| Variable | Défaut | Rôle |
|----------|--------|------|
| `CAMWATER_HOST` | `0.0.0.0` | Interface d'écoute |
| `CAMWATER_PORT` | `5050` | Port TCP |
| `CAMWATER_DEBUG` | `1` | Mode debug (mettre `0` en production) |

Exemple production locale :

```bash
CAMWATER_DEBUG=0 python3 app.py
```

---

## Exposer l'application à distance (agents en autre ville)

L'application tourne sur un PC au siège. Les agents de terrain doivent pouvoir
s'y connecter depuis n'importe où par internet. Trois options :

### Option A — Cloudflare Tunnel (recommandé, gratuit, rapide)

1. Installer `cloudflared` :
   ```bash
   brew install cloudflared          # macOS
   # ou : https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
   ```
2. Authentifier (une fois) :
   ```bash
   cloudflared tunnel login
   ```
3. Démarrer un tunnel vers l'app locale :
   ```bash
   cloudflared tunnel --url http://localhost:5050
   ```
   Cloudflare imprime une URL publique HTTPS type
   `https://xxxx-yyyy.trycloudflare.com` → à communiquer aux agents.

Pour un nom de domaine stable (recommandé pour production) :
```bash
cloudflared tunnel create camwater
cloudflared tunnel route dns camwater camwater.exemple-domaine.com
```

### Option B — ngrok (gratuit, plus simple)

```bash
brew install ngrok
ngrok config add-authtoken <votre-token>
ngrok http 5050
```
→ fournit une URL `https://xxxx.ngrok-free.app`.

### Option C — Déploiement cloud permanent

- Render.com, Railway.app, PythonAnywhere : hébergement Python gratuit/bas coût
- VPS (DigitalOcean, Hetzner, Scaleway ~5 €/mois) : contrôle total
- Conseillé si usage 24/7 avec nombreux agents

Dans ces cas, prévoir :
- Base de données persistante (volume attaché)
- Serveur WSGI en production (`gunicorn app:app` au lieu de `app.run`)
- Certificat SSL (géré par la plateforme)
- Sauvegarde régulière du fichier `data/camwater.db`

---

## Sécurité minimale recommandée en production

1. Passer `CAMWATER_DEBUG=0` (pas de page de debug exposée)
2. Changer `app.secret_key` dans `app.py` par une valeur longue et aléatoire,
   stockée en variable d'environnement
3. Utiliser un reverse proxy HTTPS (Cloudflare Tunnel le fait nativement)
4. Ajouter une règle pare-feu limitant l'accès direct au port 5050 (n'autoriser
   que Cloudflare si tunnel utilisé)
5. Sauvegarde automatique de `data/camwater.db` (cron / rclone)

---

## Test du contrôle d'accès

Après connexion en tant qu'agent terrain (`/recettes-jour` → formulaire), toute
tentative d'aller sur `/dashboard`, `/consultations/...`, `/saisie/...` doit :
- Rediriger vers `/terrain` si navigation classique
- Renvoyer un `403` JSON si c'est un appel API

Se déconnecter : bouton « Se déconnecter » sur `/terrain`, ou visite directe
de `/api/logout`.
