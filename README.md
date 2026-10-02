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

La création d'un run ne lance pas automatiquement l'exécution. Cette séparation
permet de préparer et vérifier les fichiers avant de démarrer Terraform.

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
d'intégration PostgreSQL) et vérifie la configuration Docker Compose.
