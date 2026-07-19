from datetime import datetime
from typing import Literal

from pydantic import Field, BaseModel


class ActiveWindowEvent(BaseModel):
    """
    Legacy version of `ActiveWindowEventV1`

    Please see definition of `ActiveWindowEventV1` for a general description.
    """
    time: datetime = Field(
        title="Time",
        description="Date and time when the event is recorded.",
        examples=["2026-07-17T12:00:00.000000000+00:00"],
    )
    duration: int = Field(
        title="Duration (in seconds)",
        description="Inferred duration for which the window was active - Moonwatch samples at frequent regular "
                    "intervals and we assume that the window was active during the whole sampling interval.",
        ge=0,
    )
    hostname: str = Field(
        title="Host name",
        description="Name of the computer where the event was sampled.",
    )
    username: str = Field(
        title="User name",
        description="Name of the user logged into the desktop session where the event was sampled.",
    )
    idle_for: int = Field(
        title="Idle for (in seconds)",
        description="Amount of time since last user interaction at `time`. This can be subsequently used "
                    "to filter out periods of inactivity from the logs.",
        ge=0,
    )
    process_path: str | None = Field(
        title="Process path",
        description="Absolute path to process binary of the active window. This might be null if "
                    "the path was redacted according to Moonwatch config before the log was written.",
    )
    tags: list[str] = Field(
        title="Tags",
        description="Array of string tags that are user-assigned to the event based on Moonwatch config.",
        default_factory=list,
    )
    type: Literal["ActiveWindowEvent"] = "ActiveWindowEvent"
