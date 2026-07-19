from pathlib import Path
from typing import Iterator

from pydantic_yaml import parse_yaml_file_as

from moonwatch.common import PathOrStr
from moonwatch.errors import BadConfigError
from moonwatch.logs import MoonwatchLog
from moonwatch.models.config.PreprocessingConfig import PreprocessingConfig
from moonwatch.models.config.PostprocessingConfig import PostprocessingConfig
from moonwatch.models.config.MainConfig import MainConfig


class MoonwatchConfig:
    def __init__(self, config_path: PathOrStr | None = None) -> None:
        if config_path is None:
            config_path = Path.home().resolve().joinpath(".moonwatch-rs", "config.yaml")
        else:
            config_path = Path(config_path).resolve()

        if not config_path.exists():
            raise BadConfigError(f"Cannot find main config in path: {config_path}")

        self.config_path = config_path

        with self.config_path.open(encoding="utf-8") as fp:
            try:
                self.main_config = parse_yaml_file_as(MainConfig, fp)
            except Exception as e:
                raise BadConfigError(f"Cannot parse main config in path: {config_path}") from e

        if (path := self.main_config.preprocessingConfigPath) is not None:
            abspath = self._join_path_with_moonwatch_home(path)
            if not abspath.exists():
                raise BadConfigError(f"Cannot find preprocessing config in path: {abspath}")

            with abspath.open(encoding="utf-8") as fp:
                try:
                    self.preprocessing_config = parse_yaml_file_as(PreprocessingConfig, fp)
                except Exception as e:
                    raise BadConfigError(f"Cannot parse preprocessing config in path: {abspath}") from e
        else:
            self.preprocessing_config = PreprocessingConfig()

        if (path := self.main_config.postprocessingConfigPath) is not None:
            abspath = self._join_path_with_moonwatch_home(path)
            if not abspath.exists():
                raise BadConfigError(f"Cannot find postprocessing config in path: {abspath}")

            with abspath.open(encoding="utf-8") as fp:
                try:
                    self.postprocessing_config = parse_yaml_file_as(PostprocessingConfig, fp)
                except Exception as e:
                    raise BadConfigError(f"Cannot parse postprocessing config in path: {abspath}") from e
        else:
            self.postprocessing_config = PostprocessingConfig()

    @property
    def output_dir(self) -> Path:
        return self._join_path_with_moonwatch_home(self.main_config.logDirectory)

    def _join_path_with_moonwatch_home(self, path: PathOrStr) -> Path:
        return self.config_path.parent.joinpath(path)

    def iter_logs(self) -> Iterator[MoonwatchLog]:
        yield from (MoonwatchLog(path) for path in self.output_dir.rglob("*.jsonl"))
        yield from (MoonwatchLog(path) for path in self.output_dir.rglob("*.jsonl.gz"))

    def __repr__(self) -> str:
        return f"MoonwatchConfig({str(self.config_path)!r})"
