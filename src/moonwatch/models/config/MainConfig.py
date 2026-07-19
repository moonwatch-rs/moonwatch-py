from pydantic import BaseModel, Field


class MainConfig(BaseModel):
    """
    This is the entrypoint to Moonwatch configuration.

    It describes how events are logged and stored on this particular machine.
    This top-level configuration should not be shared among different machines.

    More detailed configuration of event gathering and post-hoc analytics
    lives in separate linked configuration files - it is useful to share
    these if you have Moonwatch on multiple machines.
    """
    logDirectory: str = Field(
        title="Log directory",
        description="Path to directory where all Moonwatch logs are stored. "
                    "This will typically point to some kind of synchronized directory across devices. "
                    "Relative path is interpreted as relative to the directory with this configuration file.",
        examples=["./logs"],
    )
    logOutputSubdirectory: str = Field(
        title="Log subdirectory for this instance",
        description="Subdirectory of `logDirectory` where logs gathered from this computer will be stored. "
                    "This is optional - you can use '.' to just put all logs into one directory.",
        examples=[".", "workstation", "laptop"],
    )
    sampleEverySec: int = Field(
        title="Event sampling period (in seconds)",
        description="This parameter defines how often the active window is queried, producing a `ActiveWindowEvent` "
                    "entry in the output log.",
        examples=["15"],
    )
    writeEverySec: int = Field(
        title="Log write period (in seconds)",
        description="The background service gathers events in memory and in regular intervals writes the current "
                    "buffer to a new file, clearing the memory buffer. This should be relatively infrequent, "
                    "as to prevent creating needlessly many files. Important note - there are problems with "
                    "graceful shutdown on Windows, so the last run may be lost. Due to this problem, the default "
                    "write period is much shorter than on Linux.",
        examples=["1200", "21600"]
    )
    preprocessingConfigPath: str | None = Field(
        title="Path to preprocessing config",
        description="This configuration file describes how the Moonwatch service processes events before "
                    "they are written to the log (tagging, redacting). See definition of `PreprocessingConfig`. "
                    "Relative path is interpreted as relative to the directory with this configuration file; "
                    "it can be useful to put this into a synchronized directory so that all instances can use the same "
                    "configuration.",
        examples=["./preprocessing.yaml"]
    )
    postprocessingConfigPath: str | None = Field(
        title="Path to postprocessing config",
        description="This configuration file describes how the log data is ingested for analysis "
                    "(removing intervals without user interaction, categorizing, etc.). See definition "
                    "of `PostprocessingConfig`. "
                    "Relative path is interpreted as relative to the directory with this configuration file; "
                    "it can be useful to put this into a synchronized directory so that all instances can use the same "
                    "configuration."
        ,
        examples=["./postprocessing.yaml"]
    )
