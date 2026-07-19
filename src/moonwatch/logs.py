from abc import ABC, abstractmethod
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
from typing import Iterator, TextIO, Callable
import gzip

import polars as pl
import polars.datatypes as pt
import polars.selectors as cs

from moonwatch.common import PathOrStr
from moonwatch.models import MoonwatchEvent, _MoonwatchEvent, KNOWN_EVENT_TYPES


UNIFIED_ACTIVE_EVENT_SCHEMA = pl.Schema({  # type: ignore[arg-type]
    "time": pt.Datetime(),
    "duration": pt.Duration(),
    "hostname": pt.String,
    "username": pt.String,
    "idleFor": pt.Duration(),
    "name": pt.String,
    "category": pt.String,
    "processPath": pt.String,
    "processName": pt.String,
    "applicationLabel": pt.String,
    "applicationId": pt.String,
    "ignore": pt.Boolean,
    "isMobile": pt.Boolean,
    "tags": pt.List(pt.String),
})


class MoonwatchLog:
    _MOONWATCH_SCHEMA_RAW = pl.Schema({  # type: ignore[arg-type]
        "type": pt.Enum(KNOWN_EVENT_TYPES),
        "time": pt.Datetime(),
        "duration": pt.Int32,
        "hostname": pt.String,
        "username": pt.String,
        "idle_for": pt.Int32,
        "idleFor": pt.Int32,
        "process_path": pt.String,
        "processPath": pt.String,
        "applicationLabel": pt.String,
        "applicationId": pt.String,
        "tags": pt.List(pt.String),
    })

    def __init__(self, path: PathOrStr) -> None:
        self.path = Path(path)

    @contextmanager
    def open(self) -> Iterator[TextIO]:
        match self.path.suffixes:
            case (".jsonl",):
                with self.path.open(encoding="utf-8") as fp:
                    yield fp
            case (".jsonl", ".gz"):
                with gzip.open(self.path, "rt", encoding="utf-8") as fp:
                    yield fp
            case _:
                raise NotImplementedError(f"Unsupported file extension: {self.path}")

    def iter_models(self) -> Iterator[_MoonwatchEvent]:
        with self.open() as fp:
            for line in fp:
                yield MoonwatchEvent.validate_json(line)

    def read_df(self) -> pl.DataFrame:
        with self.open() as fp:
            df = (
                pl.read_ndjson(fp)
                .unnest(cs.matches("^data$"))
                .cast({cs.matches(f"^{k}$"): v for k, v in self._MOONWATCH_SCHEMA_RAW.items()})
            )
            for column_name_seconds in ("duration", "idle_for", "idleFor"):
                if column_name_seconds in df.columns:
                    df = df.with_columns(
                        pl.duration(seconds=column_name_seconds)
                        .alias(column_name_seconds)
                    )
            return df

    def __repr__(self) -> str:
        return f"MoonwatchLog({str(self.path)!r})"


class MoonwatchLogDataframeParser:
    def __init__(self, logs: Iterator[MoonwatchLog]) -> None:
        self.logs = list(logs)
        self._path_to_raw_df: dict[Path, pl.DataFrame] = {}

    @cached_property
    def active_window_event_df(self) -> pl.DataFrame:
        return _ActiveWindowEventV1DataframeParser(self).get_df()

    @cached_property
    def active_activity_event_df(self) -> pl.DataFrame:
        return _ActiveActivityEventV1DataframeParser(self).get_df()

    @cached_property
    def unified_active_event_df(self) -> pl.DataFrame:
        return pl.concat([
            _ActiveWindowEventV1DataframeParser(self).get_unified_df(),
            _ActiveActivityEventV1DataframeParser(self).get_unified_df(),
        ])

    @cached_property
    def device_unlock_event_df(self) -> pl.DataFrame:
        return _DeviceUnlockEventV1DataframeParser(self).get_df()

    def _iter_df(self) -> Iterator[tuple[Path, pl.DataFrame]]:
        for log in self.logs:
            if log.path not in self._path_to_raw_df:
                with log.open() as fp:
                    self._path_to_raw_df[log.path] = pl.read_ndjson(fp)

            yield log.path, self._path_to_raw_df[log.path]

    def __repr__(self) -> str:
        return f"<MoonwatchLogDataframeParser with {len(self.logs)} logs>"


class _EventDataframeParserBase(ABC):
    def __init__(self, parser: MoonwatchLogDataframeParser) -> None:
        self.parser = parser
        self.event_types: dict[str, Callable[[pl.DataFrame], pl.DataFrame]] = {}
        self.register_events()

    def get_df(self) -> pl.DataFrame:
        chunks: list[pl.DataFrame] = []

        for path, raw_df in self.parser._iter_df():
            for event_type, convert_fn in self.event_types.items():
                df = raw_df.filter(type=event_type)
                if not df.is_empty():
                    try:
                        chunks.append(convert_fn(df))
                    except Exception as e:
                        e.add_note(f"{path=}")
                        e.add_note(f"{event_type=}")
                        raise e

        schema = self.get_schema()
        return pl.concat(chunks, rechunk=True).cast(schema).select(schema.keys())

    @abstractmethod
    def register_events(self) -> None:
        pass

    @abstractmethod
    def get_schema(self) -> pl.Schema:
        pass


class _ActiveWindowEventV1DataframeParser(_EventDataframeParserBase):
    def register_events(self) -> None:
        self.event_types["ActiveWindowEventV1"] = self._convert_v1_df
        self.event_types["ActiveWindowEvent"] = self._convert_non_v1_df

    def get_schema(self) -> pl.Schema:
        return pl.Schema({  # type: ignore[arg-type]
            "time": pt.Datetime(),
            "duration": pt.Duration(),
            "hostname": pt.String,
            "username": pt.String,
            "idleFor": pt.Duration(),
            "processPath": pt.String,
            "processName": pt.String,
            "tags": pt.List(pt.String),
        })

    def get_unified_df(self) -> pl.DataFrame:
        df = self.get_df()
        return (
            df.select(
                pl.col("time"),
                pl.col("duration"),
                pl.col("hostname"),
                pl.col("username"),
                pl.col("idleFor"),
                pl.col("processName").alias("name"),
                pl.col("processPath"),
                pl.col("processName"),
                pl.lit(None).cast(pt.String).alias("applicationLabel"),
                pl.lit(None).cast(pt.String).alias("applicationId"),
                pl.lit(None).cast(pt.String).alias("category"),
                pl.lit(False).alias("ignore"),
                pl.lit(False).alias("isMobile"),
                pl.col("tags"),
            )
            .cast(UNIFIED_ACTIVE_EVENT_SCHEMA)
            .select(UNIFIED_ACTIVE_EVENT_SCHEMA.keys())
        )

    def _convert_non_v1_df(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.select(
            pl.col("time").cast(pt.Datetime),
            pl.duration(seconds=pl.col("duration")).alias("duration"),
            pl.col("hostname").cast(pt.String),
            pl.col("username").cast(pt.String),
            pl.duration(seconds=pl.col("idle_for")).alias("idleFor"),
            pl.col("process_path").cast(pt.String).alias("processPath"),
            self._process_path_to_name("process_path"),
            pl.col("tags").cast(pl.List(pl.String)),
        )

    def _convert_v1_df(self, df: pl.DataFrame) -> pl.DataFrame:
        return (
            df.unnest("data")
            .select(
                pl.col("time").cast(pt.Datetime),
                pl.duration(seconds=pl.col("duration")).alias("duration"),
                pl.col("hostname").cast(pt.String),
                pl.col("username").cast(pt.String),
                pl.duration(seconds=pl.col("idleFor")).alias("idleFor"),
                pl.col("processPath").cast(pt.String),
                self._process_path_to_name("processPath"),
                pl.col("tags").cast(pl.List(pl.String)),
            )
        )

    @staticmethod
    def _process_path_to_name(process_path_column_name: str) -> pl.Expr:
        return (
            pl.col(process_path_column_name)
            .cast(pt.String)
            .str.extract(r"([^\\/]+)$")
            .str.replace(r"(?i)\.(exe|bat|ps1|com|sh|bin)$", "")
            .str.to_lowercase()
            .alias("processName")
        )


class _ActiveActivityEventV1DataframeParser(_EventDataframeParserBase):
    def register_events(self) -> None:
        self.event_types["ActiveActivityEventV1"] = self._convert_v1_df

    def get_schema(self) -> pl.Schema:
        return pl.Schema({  # type: ignore[arg-type]
            "time": pt.Datetime(),
            "duration": pt.Duration(),
            "hostname": pt.String,
            "applicationLabel": pt.String,
            "applicationId": pt.String,
        })

    def get_unified_df(self) -> pl.DataFrame:
        df = self.get_df()
        return (
            df.select(
                pl.col("time"),
                pl.col("duration"),
                pl.col("hostname"),
                pl.lit(None).cast(pt.String).alias("username"),
                pl.lit(None).cast(pt.Duration).alias("idleFor"),
                pl.col("applicationLabel").str.to_lowercase().alias("name"),
                pl.lit(None).cast(pt.String).alias("processPath"),
                pl.lit(None).cast(pt.String).alias("processName"),
                pl.col("applicationLabel"),
                pl.col("applicationId"),
                pl.lit(None).cast(pt.String).alias("category"),
                pl.lit(False).alias("ignore"),
                pl.lit(True).alias("isMobile"),
                pl.lit([]).cast(pt.List(pt.String)).alias("tags"),
            )
            .cast(UNIFIED_ACTIVE_EVENT_SCHEMA)
            .select(UNIFIED_ACTIVE_EVENT_SCHEMA.keys())
        )

    def _convert_v1_df(self, df: pl.DataFrame) -> pl.DataFrame:
        return (
            df.unnest("data")
            .select(
                pl.col("time").cast(pt.Datetime),
                pl.duration(seconds=pl.col("duration")).alias("duration"),
                pl.col("hostname").cast(pt.String),
                pl.col("applicationLabel").cast(pt.String),
                pl.col("applicationId").cast(pt.String),
            )
        )


class _DeviceUnlockEventV1DataframeParser(_EventDataframeParserBase):
    def register_events(self) -> None:
        self.event_types["DeviceUnlockEventV1"] = self._convert_v1_df

    def get_schema(self) -> pl.Schema:
        return pl.Schema({  # type: ignore[arg-type]
            "time": pt.Datetime(),
            "hostname": pt.String,
        })

    def _convert_v1_df(self, df: pl.DataFrame) -> pl.DataFrame:
        return (
            df.unnest("data")
            .select(
                pl.col("time").cast(pt.Datetime),
                pl.col("hostname").cast(pt.String),
            )
        )
