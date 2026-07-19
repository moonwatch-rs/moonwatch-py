from typing import Optional, Literal, Annotated, Union

from pydantic import BaseModel, Field


class PostprocessingConfig(BaseModel):
    """
    This configuration file describes how logs are ingested for analytics

    Ingestion workflow for `ActiveWindowEvent`/`ActiveActivityEvent` is structured like this:
        - merge desktop and mobile events into a unified table (`ActiveEvent`)
        - run `activeEventActions` in order of definition (optional)
        - convert tag array into boolean columns
        - split long events to enforce maximum duration (optional)
        - sort by time
    """
    activeEventActions: list["PostprocessingConfigActiveEventAction"] = Field(
        title="Active event actions",
        description="This describes how to transform unified `ActiveEvent` "
                    "(desktop `ActiveWindowEvent` + mobile `ActiveActivityEvent`).",
        default_factory=list,
    )
    activeEventMaxDurationSec: int | None = Field(
        title="Maximum duration of one `ActiveEvent` (in seconds)",
        description="When set, long events derived from `ActiveActivityEvent` will be split into "
                    "multiple shorter ones so that data aggregation is easier. "
                    "This is only a concern for `ActiveActivityEvent` (which gets true duration "
                    "from the Android OS), not for `ActiveWindowEvent` (which is sampled at regular, "
                    "short intervals).",
        default=None,
    )


PostprocessingConfigActiveEventAction = Annotated[
    Union[
        "PostprocessingConfigActiveEventIgnoreAction",
        "PostprocessingConfigActiveEventAddTagAction",
        "PostprocessingConfigActiveEventSetAttributeAction",
    ],
    Field(discriminator="action")
]


class PostprocessingConfigActiveEventIgnoreAction(BaseModel):
    """
    Action to mark events as ignored (eg. for events when user is idle for a long time)
    """
    when: "PostprocessingConfigActiveEventPredicate" = Field(
        title="When (predicate)",
        description="Predicate for events that should be marked as ignored.",
    )
    exclude: Optional["PostprocessingConfigActiveEventPredicate"] = Field(
        title="Exclude (negative predicate)",
        description="Predicate for exceptions to the rule - these events will not be marked as ignored "
                    "even though they match `when`.",
        default=None,
    )
    action: Literal["ignore"] = Field(
        title="Action",
        default="ignore",
    )


class PostprocessingConfigActiveEventAddTagAction(BaseModel):
    """
    Action to add a tag to events
    """
    tag: str = Field(
        title="Tag",
        description="The tag that should be appended to `tags` array.",
    )
    when: "PostprocessingConfigActiveEventPredicate" = Field(
        title="When (predicate)",
        description="Predicate for events that should be tagged.",
    )
    exclude: Optional["PostprocessingConfigActiveEventPredicate"] = Field(
        title="Exclude (negative predicate)",
        description="Predicate for exceptions to the rule - these events will not be tagged "
                    "even though they match `when`.",
        default=None,
    )
    action: Literal["addTag"] = Field(
        title="Action",
        default="addTag",
    )


class PostprocessingConfigActiveEventSetAttributeAction(BaseModel):
    """
    Action to set unified action event string attribute
    """
    attribute: Literal["name", "category"] = Field(
        title="Attribute name",
        description="Which unified event string attribute to set (either `name` or `category`).",
    )
    value: str = Field(
        title="Attribute value",
        description="Value for the attribute.",
    )
    when: "PostprocessingConfigActiveEventPredicate" = Field(
        title="When (predicate)",
        description="Predicate for events where the attribute should be set.",
    )
    exclude: Optional["PostprocessingConfigActiveEventPredicate"] = Field(
        title="Exclude (negative predicate)",
        description="Predicate for exceptions to the rule - these events will not get the attribute value "
                    "even though they match `when`.",
        default=None,
    )
    action: Literal["setAttribute"] = Field(
        title="Action",
        default="setAttribute",
    )


class PostprocessingConfigActiveEventPredicate(BaseModel):
    """
    A predicate matching unified `ActiveEvent` (desktop `ActiveWindowEvent` + mobile `ActiveActivityEvent`)
    """
    logic: Literal["and", "or"] = Field(
        title="Logical operator",
        description="When multiple predicate attributes are used, this decides how they should be evaluated (AND, OR).",
        default="and",
    )

    name: str | None = Field(
        title="Program name",
        description="A regular expression matching the `name` attribute "
                    "(which is derived from `processName` and `applicationLabel` depending on the platform).",
        default=None,
    )
    category: str | None = Field(
        title="Category attribute",
        description="An exact string matching the `category` attribute.",
        default=None,
    )
    processPath: str | None = Field(
        title="Process path attribute (desktop only)",
        description="A regular expression matching the `processPath` attribute.",
        default=None,
    )
    processName: str | None = Field(
        title="Process name attribute (desktop only)",
        description="A regular expression matching the `processName` attribute "
                    "(last segment of `processPath`, without file extension, converted to lowercase).",
        default=None,
    )
    applicationLabel: str | None = Field(
        title="Application label attribute (mobile only)",
        description="A regular expression matching the `applicationLabel` attribute.",
        default=None,
    )
    applicationId: str | None = Field(
        title="Application ID attribute (mobile only)",
        description="An exact string matching the `applicationId` attribute.",
        default=None,
    )
    hasTag: str | None = Field(
        title="Has tag",
        description="Checks presence of given string in the `tags` array attribute.",
        default=None,
    )
    isMobile: bool | None = Field(
        title="Is mobile",
        description="Matches the `isMobile` attribute.",
        default=None,
    )
    idleForGreaterThanSec: int | None = Field(
        title="Idle for greater than given amount of seconds (desktop only)",
        description="Matches if `idleFor` attribute exceeds given limit in seconds.",
        default=None,
        gt=0,
    )
