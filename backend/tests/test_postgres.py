"""PostgreSQL integration tests for domain constraints and indexes."""
import os

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Pipeline, Project, Run, User, Validation


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Set TEST_DATABASE_URL to run PostgreSQL integration tests",
)


@pytest.fixture(scope="module")
def postgres_engine():
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def postgres_session(postgres_engine):
    with Session(postgres_engine) as session:
        yield session
        session.rollback()


def test_postgres_domain_constraints_reject_invalid_status(postgres_session: Session):
    """PostgreSQL must reject statuses outside the domain contract."""
    user = User(
        username="postgres_constraint_user",
        email="postgres_constraint@example.com",
        hashed_password="test-hash",
    )
    postgres_session.add(user)
    postgres_session.flush()
    project = Project(name="Postgres Project", owner_id=user.id)
    postgres_session.add(project)
    postgres_session.flush()
    pipeline = Pipeline(name="Postgres Pipeline", project_id=project.id)
    postgres_session.add(pipeline)
    postgres_session.flush()

    postgres_session.add(Run(pipeline_id=pipeline.id, status="not-a-status"))
    with pytest.raises(IntegrityError):
        postgres_session.flush()
    postgres_session.rollback()


def test_postgres_indexes_exist(postgres_engine):
    """Common foreign-key and status lookups must be indexed."""
    inspector = inspect(postgres_engine)
    run_indexes = {index["name"] for index in inspector.get_indexes("runs")}
    deployment_indexes = {
        index["name"] for index in inspector.get_indexes("deployments")
    }
    validation_indexes = {
        index["name"] for index in inspector.get_indexes("validations")
    }

    assert "ix_runs_pipeline_id" in run_indexes
    assert "ix_runs_status" in run_indexes
    assert "ix_deployments_run_id" in deployment_indexes
    assert "ix_deployments_status" in deployment_indexes
    assert "ix_validations_run_id" in validation_indexes
    assert "ix_validations_status" in validation_indexes
