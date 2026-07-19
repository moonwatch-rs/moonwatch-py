from datetime import datetime
from typing import Literal

from pydantic import Field, BaseModel


class ActiveActivityEventV1(BaseModel):
    """
    An event describing that an app was in the foreground (mobile only)

    This event is gathered by the mobile app and is based on OS tracking, which means
    that the recorded duration is variable (unlike the equivalent desktop event).
    There is a setting in `PostprocessingConfig` to enforce maximum duration for
    mobile events, which splits them into shorter segments that are more handy
    for resampling.

    For a desktop sibling event, see `ActiveWindowEventV1`.
    """
    time: datetime = Field(
        title="Time",
        description="Date and time when the event is recorded - this records when the activity started.",
        examples=["2026-07-17T12:00:00.000000000+00:00"],
    )
    data: "ActiveActivityEventV1Data"
    type: Literal["ActiveActivityEventV1"] = "ActiveActivityEventV1"


class ActiveActivityEventV1Data(BaseModel):
    duration: int = Field(
        title="Duration (in seconds)",
        description="Duration for which the Android app window (activity) was in the foreground. "
                    "Since this is based on OS tracking, it is a precise value with no particular upper bound.",
        ge=0
    )
    hostname: str = Field(
        title="Host name",
        description="Name of the phone where the event was sampled.",
    )
    applicationLabel: str = Field(
        title="Application label",
        description="Human-readable label of the app to which the activity belongs.",
        examples=["Firefox"],
    )
    applicationId: str = Field(
        title="Application ID",
        description="Dot-separated ID of the app to which the activity belongs.",
        examples=["org.mozilla.firefox"],
    )
