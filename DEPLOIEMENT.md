# Guide de déploiement — Vendi Market

Ce guide déploie le backend (FastAPI + PostgreSQL) sur **Railway** et le
frontend (React) sur **Vercel**. Les deux ont un plan gratuit suffisant pour
démarrer et tester avec de vrais utilisateurs. Temps estimé: 15-20 minutes.

Alternative équivalente: **Fly.io** pour le backend, **Netlify** pour le
frontend — la logique est la même, seule l'interface change.

---

## 1. Déployer le backend sur Railway

1. Crée un compte sur [railway.app](https://railway.app) (connexion GitHub recommandée).
2. Pousse le dossier `backend/` sur un dépôt GitHub (crée un repo, `git init`, `git add .`, `git commit`, `git push`).
3. Dans Railway: **New Project → Deploy from GitHub repo** → sélectionne ton repo.
4. Railway détecte le `Dockerfile` automatiquement et build l'image.
5. **Ajoute une base de données**: dans le projet Railway, clique **New → Database → PostgreSQL**. Railway crée la base et expose une variable `DATABASE_URL` automatiquement.
6. **Variables d'environnement** du service backend (onglet Variables):
   - `DATABASE_URL` → copie la valeur générée par le plugin PostgreSQL Railway (elle utilise le format `postgresql://...`; remplace le préfixe par `postgresql+psycopg2://` pour que SQLAlchemy fonctionne)
   - `JWT_SECRET_KEY` → génère une vraie valeur aléatoire:
     ```
     python3 -c "import secrets; print(secrets.token_urlsafe(64))"
     ```
   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `CORS_ORIGINS=["https://ton-app.vercel.app"]` (l'URL du frontend, à mettre à jour après l'étape 2)
   - Toutes les autres variables de `.env.example` (frais, devise, etc.) — copie-les telles quelles, les valeurs par défaut conviennent pour démarrer.
7. Railway te donne une URL publique du type `https://ton-projet.up.railway.app`. Note-la.
8. **Appliquer les migrations**: dans l'onglet Railway du service, ouvre un terminal (ou utilise `railway run`) et exécute:
   ```
   alembic upgrade head
   python -m app.seeds.seed_taxonomy
   ```
9. Vérifie: `https://ton-projet.up.railway.app/health` doit répondre `{"status":"ok",...}`.

---

## 2. Déployer le frontend sur Vercel

1. Crée un compte sur [vercel.com](https://vercel.com) (connexion GitHub recommandée).
2. Pousse le dossier `frontend/` sur un dépôt GitHub (même logique qu'à l'étape 1 — peut être un dossier du même repo ou un repo séparé).
3. Dans Vercel: **Add New → Project** → sélectionne ton repo. Vercel détecte Vite automatiquement.
4. **Variable d'environnement** (Settings → Environment Variables):
   - `VITE_API_URL` = `https://ton-projet.up.railway.app/api/v1` (l'URL Railway de l'étape 1, avec `/api/v1` à la fin)
5. Déploie. Vercel te donne une URL du type `https://ton-app.vercel.app`.
6. **Reviens sur Railway** et mets à jour `CORS_ORIGINS` avec cette URL exacte, puis redéploie le backend pour que les requêtes du frontend soient acceptées.

---

## 3. Vérification finale

Ouvre `https://ton-app.vercel.app` sur ton téléphone. Le parcours complet
doit fonctionner: créer un compte, publier un article, le retrouver dans le
feed, faire une offre depuis un autre compte, l'accepter, payer (mock),
expédier, confirmer réception, laisser un avis.

---

## Nom de domaine personnalisé (optionnel)

Une fois que tu as acheté un domaine pour Vendi Market (ex. via Namecheap,
environ 10-15$/an pour un `.com`, ou un `.ci` via un registrar local
ivoirien si disponible):

- Sur Vercel: Settings → Domains → ajoute ton domaine, suis les instructions DNS.
- Sur Railway: Settings → Networking → Custom Domain, même logique pour l'API si tu veux une URL type `api.tonapp.com`.

---

## Coûts à prévoir

- Railway: gratuit avec un crédit limité mensuel, puis facturation à l'usage (généralement quelques dollars/mois pour ce volume au démarrage).
- Vercel: gratuit pour ce type de projet tant que le trafic reste modéré.
- Nom de domaine: ~10-15$/an si tu en prends un.
- **Rien à payer pour Wave/Orange Money/MTN tant que le paiement reste en mode mock** — ces coûts (frais de transaction, éventuel abonnement) n'arrivent que lorsque tu signes avec un vrai provider.

## Ce qui reste 100% de ton côté (rappel)

- Créer les comptes Railway/Vercel/GitHub eux-mêmes
- Le nom de domaine et son achat
- Toute négociation avec Wave/Orange Money/MTN pour sortir du mode mock
- Les comptes développeur Apple/Google si tu veux la version app store plus tard
- Les CGU / politique de confidentialité / statut légal de l'entreprise
