from datetime import datetime, timedelta

from pydantic import Field, BaseModel


class ActiveEventV1(BaseModel):
    """
    This event describes intermediate representation after `ActiveWindowEvent` + `ActiveActivityEvent` unification

    There are no actual JSON data with this schema, it describes shape of the dataframe that is created
    during postprocessing. These are the fields that actions defined in `PostprocessingConfig` refer to.

    """
    time: datetime = Field(
        title="Time",
        description="Date and time when the event is recorded.",
    )
    duration: timedelta = Field(
        title="Duration",
        description="Duration for which the application window was in the foreground.",
    )
    hostname: str = Field(
        title="Host name",
        description="Name of the desktop/phone where the event was sampled.",
    )
    username: str | None = Field(
        title="User name",
        description="Name of the user logged into the desktop session where the event was sampled (desktop only).",
    )
    idleFor: timedelta | None = Field(
        title="Idle for",
        description="Amount of time since last user interaction at `time` (desktop only).",
    )
    name: str = Field(
        title="Program name (unified)",
        description="Program name derived from `processName` (desktop) or `applicationLabel` (mobile). "
                    "Converted to lowercase. This should be a reasonable "
                    "first approximation that allows grouping of the same program across environments.",
    )
    category: str | None = Field(
        title="Program category (unified)",
        description="Field for user-defined category. Typically, these will be based on tags, but unlike tags, "
                    "each event can only have one category.",
    )
    processPath: str | None = Field(
        title="Process path",
        description="Absolute path to process binary of the active window (desktop only).",
    )
    processName: str | None = Field(
        title="Process name",
        description="Last path segment of `processPath`, without file extension like .exe (desktop only).",
    )
    applicationLabel: str | None = Field(
        title="Application label",
        description="Human-readable label of the app to which the activity belongs (mobile only).",
    )
    applicationId: str | None = Field(
        title="Application ID",
        description="Dot-separated ID of the app to which the activity belongs (mobile only)",
    )
    ignore: bool = Field(
        title="Ignore",
        description="Flag that prevents the event being exported. Typically you will want "
                    "to set this via action in `PostprocessingConfig` by filtering on `idleForGreaterThanSec`.",
    )
    isMobile: bool = Field(
        title="Is mobile",
        description="Flag that differentiates between event source (desktop/mobile).",
    )
    tags: list[str] = Field(
        title="Tags",
        description="Array of string tags that are user-assigned to the event.",
    )
