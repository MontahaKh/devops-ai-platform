"""Pipeline schemas."""
from datetime import datetime

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.core.domain_enums import PipelineStatus


class PipelineFile(BaseModel):
    path: str = Field(..., min_length=1, max_length=500)
    file_type: Literal["terraform", "ansible", "other"] = "terraform"
    required: bool = True


class PipelineStep(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    action: Literal["terraform_fmt", "terraform_validate", "deploy"]
    parameters: dict = Field(default_factory=dict)
    required_files: list[str] = Field(default_factory=list)


class ValidationStrategy(BaseModel):
    terraform_commands: list[Literal["fmt", "validate"]] = Field(
        default_factory=lambda: ["fmt", "validate"]
    )
    fail_on_warnings: bool = False


class PipelineDefinition(BaseModel):
    schema_version: Literal["v1"] = "v1"
    target_environment: str = Field(default="local", min_length=1, max_length=100)
    parameters: dict = Field(default_factory=dict)
    required_files: list[PipelineFile] = Field(default_factory=list)
    validation_strategy: ValidationStrategy = Field(default_factory=ValidationStrategy)
    steps: list[PipelineStep] = Field(..., min_length=1)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_definition(cls, value):
        if not value:
            return {
                "steps": [
                    {
                        "name": "terraform-validation",
                        "action": "terraform_validate",
                    }
                ]
            }
        if isinstance(value, dict) and isinstance(value.get("steps"), list):
            steps = value["steps"]
            if all(isinstance(step, str) for step in steps):
                value = {**value}
                value["steps"] = [
                    {
                        "name": step,
                        "action": "terraform_validate"
                        if step == "validate"
                        else step,
                    }
                    for step in steps
                ]
        return value


def default_pipeline_definition() -> PipelineDefinition:
    return PipelineDefinition(
        steps=[
            PipelineStep(
                name="terraform-validation",
                action="terraform_validate",
            )
        ]
    )


class PipelineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    project_id: int = Field(..., gt=0)
    definition: PipelineDefinition = Field(default_factory=default_pipeline_definition)
    status: PipelineStatus = PipelineStatus.ACTIVE


class PipelineUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    definition: PipelineDefinition | None = None
    status: PipelineStatus | None = None


class PipelineRead(BaseModel):
    id: int
    name: str
    description: str | None
    project_id: int
    definition: PipelineDefinition
    status: PipelineStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
