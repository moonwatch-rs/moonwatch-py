from datetime import datetime
from typing import Literal

from pydantic import Field, BaseModel


class ActiveWindowEventV1(BaseModel):
    """
    An event describing what window was active (desktop only)

    This event is gathered by the desktop app and is based on sampling in regular intervals;
    we do not actually know how long each window is in the foreground, but we guess based on
    how many times we "catch it" being active and what the sampling interval is.

    Moonwatch samples process path and window name - please see `PreprocessingConfig` definition
    for ways to customize what data gets logged and how. As a hard rule, window names are never logged;
    they can only be used as a predicate in the preprocessing config.

    Moonwatch does not have any further insight into the active window beyond its title and process path.
    This is by design - chiefly to reduce Moonwatch's exposure to your data. As a consequence,
    visibility into complex applications - like web browsers - is limited: if you wish to get a break-down
    of websites you visit, this is only possible by setting up filters based on the website/window title
    or possibly by using different browsers for different purposes.

    For a mobile sibling event, see `ActiveActivityEventV1`.
    """
    time: datetime = Field(
        title="Time",
        description="Date and time when the event is recorded.",
        examples=["2026-07-17T12:00:00.000000000+00:00"],
    )
    data: "ActiveWindowEventV1Data"
    type: Literal["ActiveWindowEventV1"] = "ActiveWindowEventV1"


class ActiveWindowEventV1Data(BaseModel):
    duration: int = Field(
        title="Duration (in seconds)",
        description="Inferred duration for which the window was active - Moonwatch samples at frequent regular "
                    "intervals and we assume that the window was active during the whole sampling interval. "
                    "In the logs, it will look like the duration for all desktop events is the same - this is normal.",
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
    idleFor: int = Field(
        title="Idle for (in seconds)",
        description="Amount of time since last user interaction at `time`. This can be subsequently used "
                    "to filter out periods of inactivity from the logs.",
        ge=0,
    )
    processPath: str | None = Field(
        title="Process path",
        description="Absolute path to process binary of the active window. This might be null if "
                    "the path was redacted according to Moonwatch config before the log was written.",
    )
    tags: list[str] = Field(
        title="Tags",
        description="Array of string tags that are user-assigned to the event based on Moonwatch config.",
        default_factory=list,
    )
