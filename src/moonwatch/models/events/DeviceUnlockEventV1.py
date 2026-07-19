from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DeviceUnlockEventV1(BaseModel):
    """
    An event describing that a screen lock was unlocked (mobile only)

    This event is gathered by the mobile app and is based on OS tracking.
    """

    time: datetime = Field(
        title="Time",
        description="Date and time when the event is recorded.",
        examples=["2026-07-17T12:00:00.000000000+00:00"],
    )
    data: "DeviceUnlockEventV1Data"
    type: Literal["DeviceUnlockEventV1"] = "DeviceUnlockEventV1"


class DeviceUnlockEventV1Data(BaseModel):
    hostname: str = Field(
        title="Host name",
        description="Name of the phone where the event was sampled.",
    )
