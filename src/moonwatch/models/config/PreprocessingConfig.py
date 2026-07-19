from pydantic import BaseModel, Field


class PreprocessingConfig(BaseModel):
    """
    This configuration file describes how events are processed before they are committed to log file

    It's advisable to keep processing here minimal and do your categorization etc. in the postprocessing
    config, where it is flexible - processing defined here affects the data as they are being collected
    and cannot be changed retroactively.

    The main purpose of this processing stage is to take advantage of the `windowTitle` event attribute,
    which is deliberately not logged by Moonwatch, but you can tag/redact events based on it here.
    """
    activeWindowEvent: list["PreprocessingConfigActiveWindowEvent"] = Field(
        title="Filters for window events",
        description="This list is evaluated in order for each incoming `ActiveWindowEvent`.",
        default_factory=list,
    )


class PreprocessingConfigActiveWindowEvent(BaseModel):
    """
    A conditional filter for `ActiveWindowEvent` that runs given action based on a predicate.
    """
    when: "PreprocessingConfigActiveWindowEventPredicate" = Field(
        title="When (predicate)",
    )
    then: "PreprocessingConfigActiveWindowEventAction" = Field(
        title="Then (action)",
    )


class PreprocessingConfigActiveWindowEventPredicate(BaseModel):
    """
    A predicate matching `ActiveWindowEvent`

    When multiple attributes are used, it behaves as logical AND - all predicates
    must match simultaneously.
    """
    windowTitle: str | None = Field(
        title="Window title attribute",
        description="A regular expression matching the `windowTitle` attribute.",
        default=None,
    )
    processPath: str | None = Field(
        title="Process path attribute",
        description="A regular expression matching the `processPath` attribute.",
        default=None,
    )
    hasTag: str | None = Field(
        title="Has tag",
        description="Checks presence of given string in the `tags` array attribute.",
        default=None,
    )


class PreprocessingConfigActiveWindowEventAction(BaseModel):
    """
    An action modifying `ActiveWindowEvent`
    """
    addTag: str | None = Field(
        title="Add tag",
        description="Appends given string to the `tags` array attribute.",
        default=None,
    )
    clearProcessPath: bool = Field(
        title="Clear process path",
        description="Redacts the `processPath` attribute by setting it to null.",
        default=False,
    )
    delete: bool = Field(
        title="Delete event",
        description="Removes the event entirely, so it is not added to the log.",
        default=False,
    )
