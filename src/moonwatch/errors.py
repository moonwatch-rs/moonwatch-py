class MoonwatchError(Exception):
    """Base class for Moonwatch errors"""


class BadConfigError(MoonwatchError):
    pass
