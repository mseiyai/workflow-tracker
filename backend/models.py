from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints


TaskStatus = Literal["pending", "in_progress", "done"]


class CreateTaskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
    ]


class UpdateTaskStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TaskStatus


class TaskResponse(BaseModel):
    id: int
    title: str
    status: TaskStatus
