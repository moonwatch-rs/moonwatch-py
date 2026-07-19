import datetime

from pydantic_core import TzInfo
import pytest

from moonwatch.config import MoonwatchConfig
from moonwatch.models import ActiveWindowEventV1, ActiveWindowEvent, ActiveActivityEventV1, DeviceUnlockEventV1
from moonwatch.models.events.ActiveActivityEventV1 import ActiveActivityEventV1Data
from moonwatch.models.events.ActiveWindowEventV1 import ActiveWindowEventV1Data
from moonwatch.models.events.DeviceUnlockEventV1 import DeviceUnlockEventV1Data


@pytest.mark.parametrize("log_filename", ["config.yaml", "config_gzip.yaml"])
def test_read_logs(log_filename, shared_datadir):
    config_path = shared_datadir.joinpath(log_filename)
    config = MoonwatchConfig(config_path)
    logs = config.iter_logs()

    model_dict = {}
    for log in logs:
        model_dict[log.path.name.split(".")[0]] = list(log.iter_models())

    reference_model_dict = {
        "019f7184-dc2d-73f0-a3d7-a7bda1eb51a3": [
            ActiveWindowEventV1(time=datetime.datetime(2026, 7, 17, 12, 0, tzinfo=TzInfo(0)),
                                data=ActiveWindowEventV1Data(duration=15,
                                hostname='my-windows-pc', username='my-username', idleFor=0,
                                processPath='C:\\Program Files\\Mozilla Firefox\\firefox.exe', tags=[]),
                                type='ActiveWindowEventV1'),
            ActiveWindowEventV1(time=datetime.datetime(2026, 7, 17, 13, 0, tzinfo=TzInfo(0)),
                                data=ActiveWindowEventV1Data(duration=15,
                                hostname='my-windows-pc', username='my-username', idleFor=3600,
                                processPath='C:\\Program Files\\Mozilla Firefox\\firefox.exe', tags=[]),
                                type='ActiveWindowEventV1'),
        ],
        "91d2a1a54d626ab3be31189f44ea70b07bda084e": [
            ActiveWindowEvent(time=datetime.datetime(2026, 7, 16, 18, 0, tzinfo=TzInfo(0)), duration=15,
                              hostname='my-windows-pc', username='my-username', idle_for=0,
                              process_path='C:\\Program Files\\Mozilla Firefox\\firefox.exe', tags=[],
                              type='ActiveWindowEvent'),
        ],
        "afb00c63-c4bd-4af2-abcb-f56562d52720": [
            ActiveActivityEventV1(time=datetime.datetime(2026, 7, 15, 13, 0, tzinfo=TzInfo(0)),
                                  data=ActiveActivityEventV1Data(duration=250,
                                  hostname='my-android-phone', applicationLabel='Firefox',
                                  applicationId='org.mozilla.firefox'), type='ActiveActivityEventV1'),
            DeviceUnlockEventV1(time=datetime.datetime(2026, 7, 15, 12, 59, tzinfo=TzInfo(0)),
                                data=DeviceUnlockEventV1Data(hostname='my-android-phone'), type='DeviceUnlockEventV1'),
        ],
    }

    assert model_dict == reference_model_dict
