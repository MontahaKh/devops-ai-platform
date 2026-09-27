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

Adapter ensuite `DATABASE_URL` dans `backend/.env` avec les identifiants de la
base PostgreSQL locale. Ne jamais committer ce fichier.

### Migrations

Lorsque PostgreSQL est disponible :

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
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
