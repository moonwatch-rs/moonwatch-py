import json
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel

from moonwatch.common import PathOrStr
from moonwatch.models.config.MainConfig import MainConfig
from moonwatch.models.config.PreprocessingConfig import PreprocessingConfig
from moonwatch.models.config.PostprocessingConfig import PostprocessingConfig
from moonwatch.models.events.ActiveActivityEventV1 import ActiveActivityEventV1
from moonwatch.models.events.ActiveEventV1 import ActiveEventV1
from moonwatch.models.events.ActiveWindowEvent import ActiveWindowEvent
from moonwatch.models.events.ActiveWindowEventV1 import ActiveWindowEventV1
from moonwatch.models.events.DeviceUnlockEventV1 import DeviceUnlockEventV1


class SpecGenerator:
    def __init__(self, output_dir: PathOrStr = ".") -> None:
        self.output_dir = Path(output_dir)

    def run(self) -> None:
        self._dump_models(
            self.output_dir.joinpath("config"),
            (
                MainConfig,
                PreprocessingConfig,
                PostprocessingConfig,
            )
        )

        self._dump_models(
            self.output_dir.joinpath("events"),
            (
                ActiveActivityEventV1,
                ActiveEventV1,
                ActiveWindowEvent,
                ActiveWindowEventV1,
                DeviceUnlockEventV1,
            )
        )

    @staticmethod
    def _dump_models(output_dir: Path, models: Iterable[type[BaseModel]]) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        for model in models:
            json_schema_dict = model.model_json_schema()
            name = json_schema_dict["title"]
            with output_dir.joinpath(f"{name}.json").open("w", encoding="utf-8") as fp:
                json.dump(json_schema_dict, fp, indent=2)
