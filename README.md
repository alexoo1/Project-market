# Project Market — MVP Marketplace Seconde Main (Côte d'Ivoire)

Nom de code temporaire pour la marketplace de seconde main inspirée de Vinted,
pensée d'abord pour la Côte d'Ivoire. Ce dépôt contient la **Phase 1** :
architecture, infrastructure Docker/PostgreSQL, et authentification complète.

## État d'avancement

| Phase | Contenu                                              | Statut |
|-------|-------------------------------------------------------|--------|
| 1     | Architecture, Docker/PostgreSQL, auth JWT               | ✅ Fait |
| 2     | Utilisateurs, profils, catégories, annonces, feed, recherche, favoris | ✅ Fait |
| 3     | Messagerie, offres, négociation                        | ✅ Fait |
| 4     | Commandes, paiement mock, frais plateforme, livraison   | ✅ Fait |
| 5     | Avis, followers, boosts, notifications                  | ✅ Fait |
| 6     | Application web connectée au backend (mobile React Native non démarré) | ✅ Web fait |

Backend complet: 33 tests automatisés, tous validés. Frontend web: connecté
aux vraies API, build de production validé, intégration testée en conditions
réelles (backend + frontend démarrés ensemble, parcours register → feed →
création d'annonce → fiche produit → auth vérifiés).

## Architecture backend

```
backend/
  app/
    core/          # config centralisée, sécurité (JWT/bcrypt), exceptions, dependencies
    database/       # session SQLAlchemy, base déclarative, mixins (UUID, timestamps)
    models/         # modèles SQLAlchemy (User pour l'instant)
    schemas/        # schémas Pydantic (entrée/sortie API)
    repositories/    # accès aux données pur (pas de logique métier)
    services/       # logique métier, orchestration repository + sécurité
    routers/         # endpoints FastAPI (fins, délèguent aux services)
    main.py          # point d'entrée FastAPI
  alembic/           # migrations de base de données
  tests/             # tests pytest
```

Principe respecté : **aucune logique métier dans les routes**. Les routers ne
font que valider la requête (via Pydantic), appeler un service, et traduire
les exceptions métier en réponses HTTP.

## Stack technique

- **Backend** : FastAPI, SQLAlchemy 2.0, PostgreSQL, Alembic, Pydantic v2, JWT
- **Sécurité mots de passe** : `bcrypt` utilisé directement (voir note ci-dessous)
- **Infrastructure** : Docker, docker-compose

> **Note technique** : la librairie `passlib` (couramment recommandée pour le
> hashing avec FastAPI) présente une incompatibilité connue avec les versions
> récentes de `bcrypt` (`AttributeError: module 'bcrypt' has no attribute
> '__about__'`), qui casse le hashing des mots de passe en erreur 500. Ce
> projet utilise donc `bcrypt` directement (voir `app/core/security.py`),
> plus simple et sans cette dépendance fragile.

## Installation

### Prérequis
- Docker et docker-compose
- (optionnel, pour dev sans Docker) Python 3.12+, PostgreSQL 16+

### 1. Variables d'environnement

```bash
cp backend/.env.example backend/.env
```

Éditez `backend/.env` si besoin (en particulier `JWT_SECRET_KEY` avant tout
déploiement réel — ne jamais utiliser la valeur par défaut en production).

### 2. Lancement avec Docker (recommandé)

```bash
docker-compose up --build
```

Cela démarre :
- `db` : PostgreSQL sur le port 5432
- `backend` : FastAPI sur le port 8000 (rechargement automatique activé)

L'API est alors disponible sur `http://localhost:8000`, avec la
documentation interactive sur `http://localhost:8000/api/v1/docs`.

### 3. Migrations de base de données

Les migrations ne sont pas exécutées automatiquement au démarrage du
conteneur (pour garder le contrôle sur quand elles s'appliquent). Une fois
les conteneurs démarrés :

```bash
docker-compose exec backend alembic upgrade head
```

Pour créer une nouvelle migration après avoir modifié un modèle :

```bash
docker-compose exec backend alembic revision --autogenerate -m "description du changement"
docker-compose exec backend alembic upgrade head
```

### 4. Lancement backend sans Docker (développement local)

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Adapter DATABASE_URL dans .env pour pointer vers votre PostgreSQL local
alembic upgrade head
uvicorn app.main:app --reload
```

### 5. Tests

Les tests nécessitent une base PostgreSQL de test accessible (par défaut
`project_market_test`, configurable via la variable d'environnement
`DATABASE_URL` avant de lancer pytest) :

```bash
cd backend
. .venv/bin/activate
pytest tests/ -v
```

Le parcours d'authentification complet (inscription, doublon, connexion,
mauvais mot de passe, `/me`, refresh token, mot de passe oublié) est couvert
par 8 tests automatisés, tous validés.

## Endpoints disponibles

### Authentification
| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Inscription | Non |
| POST | `/api/v1/auth/login` | Connexion | Non |
| POST | `/api/v1/auth/refresh` | Renouvellement du token | Non |
| POST | `/api/v1/auth/logout` | Déconnexion | Oui |
| POST | `/api/v1/auth/forgot-password` | Mot de passe oublié | Non |
| POST | `/api/v1/auth/reset-password` | Réinitialisation | Non |
| GET | `/api/v1/auth/me` | Profil courant | Oui |

### Annonces
| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/api/v1/categories` | Liste des catégories | Non |
| GET | `/api/v1/brands` | Liste des marques | Non |
| POST | `/api/v1/listings` | Créer une annonce | Oui |
| GET | `/api/v1/listings` | Feed / recherche / filtres | Non |
| GET | `/api/v1/listings/mine` | Mes annonces | Oui |
| GET | `/api/v1/listings/{id}` | Détail d'une annonce | Non |
| PATCH | `/api/v1/listings/{id}` | Modifier (propriétaire) | Oui |
| DELETE | `/api/v1/listings/{id}` | Supprimer (propriétaire) | Oui |
| GET/PUT/DELETE | `/api/v1/favorites` | Favoris | Oui |

### Messagerie & Offres
| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST/GET | `/api/v1/conversations` | Démarrer / lister conversations | Oui |
| GET/POST | `/api/v1/conversations/{id}/messages` | Messages | Oui |
| POST | `/api/v1/listings/{id}/offers` | Faire une offre | Oui |
| PATCH | `/api/v1/offers/{id}/accept` \| `/reject` | Répondre à une offre | Oui |
| POST | `/api/v1/offers/{id}/counter` | Contre-offre | Oui |
| GET | `/api/v1/offers/mine` | Mes offres | Oui |

### Commandes
| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/v1/listings/{id}/purchase` | Achat direct | Oui |
| POST | `/api/v1/offers/{id}/purchase` | Achat via offre acceptée | Oui |
| POST | `/api/v1/orders/{id}/pay` \| `/ship` \| `/confirm-receipt` \| `/cancel` | Cycle de vie commande | Oui |
| GET | `/api/v1/orders/mine/purchases` \| `/mine/sales` | Historique | Oui |

### Avis, followers, boosts, notifications
| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/v1/orders/{id}/reviews` | Laisser un avis | Oui |
| GET | `/api/v1/users/{id}/reviews` | Avis publics | Non |
| PUT/DELETE | `/api/v1/users/{id}/follow` | Suivre / ne plus suivre | Oui |
| POST | `/api/v1/listings/{id}/boosts` | Booster une annonce | Oui |
| GET | `/api/v1/notifications` | Mes notifications | Oui |

`GET /health` (sans auth) permet de vérifier que le service tourne.

## Décisions d'architecture notables

- **UUID en clé primaire** : évite les identifiants séquentiels devinables
  pour toutes les ressources métier.
- **Tokens séparés access/refresh** : l'access token a une courte durée de
  vie (30 min par défaut), le refresh token une longue durée (30 jours).
  Chaque refresh effectue une rotation (nouveaux tokens émis).
- **Champ `jti` dans les JWT** : présent dès maintenant pour permettre une
  future révocation de tokens (ex. blocklist Redis), sans casser la
  compatibilité des tokens déjà émis.
- **OTP SMS prévu mais non actif** : le modèle `User` contient déjà
  `phone_verified_at`, et `Settings` contient les paramètres OTP
  (`OTP_ENABLED=false` par défaut). L'ajout se fera sans migration
  supplémentaire lourde.
- **Configuration centralisée** : toutes les valeurs métier (frais
  plateforme, durées de token, devise, etc.) vivent uniquement dans
  `app/core/config.py`, jamais dupliquées ailleurs dans le code.
- **`/auth/forgot-password` ne révèle jamais** si un compte existe pour
  l'identifiant fourni (protection contre l'énumération de comptes) : la
  réponse est strictement identique dans les deux cas.

## Prochaines étapes (Phase 2)

Utilisateurs déjà en place. Phase 2 ajoutera : modèles `Listing`,
`ListingImage`, `Category`, `Brand`, `Favorite`, le feed, la recherche et
les filtres, en suivant le même pattern architectural (repository →
service → router).
