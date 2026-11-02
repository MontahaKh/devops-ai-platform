# DevOps AI Platform

Plateforme DevOps assistée par intelligence artificielle pour aider à la génération, la validation et l'orchestration d'infrastructures Cloud.

## Structure initiale

- `backend/` : backend Python en FastAPI.
- `frontend/` : interface Angular.
- `infrastructure/` : Terraform, Ansible, Kubernetes et CI/CD.
- `monitoring/` : Prometheus et Grafana.
- `docs/` : architecture et UML.

## Objectif

Le projet vise à assister un ingénieur DevOps sans automatiser les décisions critiques à sa place.

## Backend

### Installation

Depuis PowerShell :

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Pour utiliser l'environnement local reproductible, les services PostgreSQL,
PostgreSQL de test et Redis sont fournis par Docker Compose :

```powershell
docker compose up -d postgres postgres-test redis
```

Le fichier `backend/.env` doit contenir les URLs locales suivantes. Ne jamais
committer ce fichier ni une vraie clé JWT :

```dotenv
DATABASE_URL=postgresql+psycopg://devops_app:change_me@localhost:5432/devops_ai_platform
TEST_DATABASE_URL=postgresql+psycopg://devops_test:change_me@localhost:5433/devops_ai_platform_test
REDIS_URL=redis://localhost:6379/0
TASK_QUEUE_ENABLED=false
```

Les mots de passe `change_me` sont des valeurs de développement uniquement.

Pour lancer l'API dans Docker sans worker Celery :

```powershell
docker compose up -d postgres redis api
```

L'API est ensuite disponible sur `http://127.0.0.1:8000`.

Pour activer l'exécution asynchrone avec Celery et Redis :

```powershell
$env:TASK_QUEUE_ENABLED="true"
docker compose up -d postgres redis api worker
```

Le worker Celery utilise Redis comme broker et backend de résultats. Les runs
créés par l'API sont alors envoyés à la file de tâches; les erreurs temporaires
sont réessayées selon `RUN_MAX_RETRIES`.

Le cycle d'exécution manuel suit cet ordre :

1. créer un run avec `POST /runs` ;
2. ajouter les fichiers Terraform avec `POST /generated-files` ;
3. lancer le run avec `POST /runs/{run_id}/execute`.
4. consulter les résultats avec `GET /runs/{run_id}/logs`.

La création d'un run ne lance pas automatiquement l'exécution. Cette séparation
permet de préparer et vérifier les fichiers avant de démarrer Terraform.

Les fichiers générés sont validés avant leur enregistrement : les chemins doivent
être relatifs et utiliser `/`, les fichiers Terraform doivent se terminer par
`.tf` ou `.tf.json`, le contenu ne doit pas être vide et sa taille est limitée
à 1 MiB.

Une stratégie de pipeline peut également inclure `plan` après `fmt` et
`validate`. Cette commande affiche les changements Terraform prévus sans
appliquer de ressources. `terraform apply` n'est pas exécuté par l'API.

### Migrations

Lorsque PostgreSQL est disponible :

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Avec Docker Compose, la commande équivalente est :

```powershell
docker compose run --rm api alembic upgrade head
```

Après une modification des modèles SQLAlchemy :

```powershell
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "description"
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### Lancement

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

L'API est disponible sur `http://127.0.0.1:8000`, sa documentation sur
`http://127.0.0.1:8000/docs` et la route de santé sur
`http://127.0.0.1:8000/health`.

### Tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

Pour exécuter les tests d'intégration PostgreSQL, démarrer le service de test
et définir `TEST_DATABASE_URL` :

```powershell
docker compose up -d postgres-test
$env:TEST_DATABASE_URL="postgresql+psycopg://devops_test:change_me@localhost:5433/devops_ai_platform_test"
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_postgres.py -q
```

Les deux tests PostgreSQL créent puis suppriment leurs tables dans une base
dédiée. Ils ne doivent pas être exécutés sur la base de développement.

Pour arrêter les services :

```powershell
docker compose down
```

Pour supprimer également les données locales des conteneurs :

```powershell
docker compose down -v
```

### CI

Le workflow GitHub Actions `.github/workflows/ci.yml` s'exécute sur les
pull requests et les pushes vers `main`. Il installe les dépendances backend,
applique les migrations PostgreSQL, exécute les tests (y compris les tests
d'intégration PostgreSQL), construit et teste le frontend Angular, puis vérifie
la configuration Docker Compose.

## Frontend Angular

Le frontend est disponible dans `frontend/`. Il contient un shell Dashboard
connecté aux routes backend pour l'authentification, les projets, les pipelines,
les runs, les fichiers Terraform et les logs de validation.

Démarrer les services backend :

```powershell
docker compose up -d postgres redis api
```

Puis démarrer Angular dans un autre terminal :

```powershell
cd frontend
npm.cmd install
npm.cmd start
```

L'interface est disponible sur `http://127.0.0.1:4200`. Le token JWT est
conservé dans le stockage local du navigateur et ajouté automatiquement aux
requêtes API. Le parcours Terraform dans l'interface respecte le cycle :

```text
Créer un pipeline -> créer un run depuis la page Runs
-> ajouter ou modifier un fichier .tf -> exécuter le run
-> suivre le statut -> consulter les logs
```

La page Runs permet de choisir le pipeline, de définir le nombre de tentatives
et le délai d'exécution, puis de suivre automatiquement un run en cours. La
page Terraform files permet de créer plusieurs fichiers `.tf`, de modifier
leur contenu et d'incrémenter leur version avant l'exécution.

Les tests frontend ciblés couvrent le chargement et la création d'un run ainsi
que l'édition et la sauvegarde d'un fichier Terraform :

```powershell
cd frontend
npm.cmd test
```

Les routes frontend actuellement disponibles sont `/login`, `/register`,
`/dashboard`, `/projects`, `/pipelines`, `/runs`, `/validation-logs`,
`/terraform-files`, `/profile`, `/admin`, `/users` et `/runs/:id/logs`.

Le frontend applique également le RBAC visible : chaque utilisateur peut
consulter et modifier son profil, tandis que les pages `/admin` et `/users`
sont réservées au rôle `admin`. L'API filtre déjà les projets, pipelines, runs,
fichiers et logs par propriétaire ; un utilisateur standard ne reçoit donc pas
les ressources des autres utilisateurs. Un administrateur peut consulter les
ressources globales et gérer les rôles depuis le centre d'administration.

La page `/register` permet maintenant de créer un compte utilisateur standard.
La création du premier administrateur est volontairement séparée de
l'inscription publique. Pour initialiser ou mettre à jour un administrateur
dans Docker, définir les variables suivantes avant le démarrage :

```powershell
$env:ADMIN_SEED_ENABLED="true"
$env:ADMIN_USERNAME="admin"
$env:ADMIN_EMAIL="admin@example.com"
$env:ADMIN_PASSWORD="change-this-password"
docker compose up -d postgres redis api
```

Le seed est idempotent : il crée le compte s'il n'existe pas et met à jour son
rôle, son mot de passe et son état actif s'il existe déjà. Ne pas utiliser un
mot de passe de développement en production.
