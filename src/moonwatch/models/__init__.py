from typing import Annotated, Union

from pydantic import Field, TypeAdapter

from moonwatch.models.events.ActiveActivityEventV1 import ActiveActivityEventV1
from moonwatch.models.events.ActiveWindowEvent import ActiveWindowEvent
from moonwatch.models.events.ActiveWindowEventV1 import ActiveWindowEventV1
from moonwatch.models.events.DeviceUnlockEventV1 import DeviceUnlockEventV1


_MoonwatchEvent = Annotated[
    Union[
        ActiveActivityEventV1,
        ActiveWindowEvent,
        ActiveWindowEventV1,
        DeviceUnlockEventV1,
    ],
    Field(discriminator="type")
]
MoonwatchEvent: TypeAdapter[_MoonwatchEvent] = TypeAdapter(_MoonwatchEvent)

KNOWN_EVENT_TYPES: list[str] = [
    "ActiveWindowEvent",
    "ActiveWindowEventV1",
    "ActiveActivityEventV1",
    "DeviceUnlockEventV1",
]
