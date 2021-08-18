import os

import pytest

from aiodeta import Deta

try:
    from dotenv import load_dotenv

    load_dotenv()
except:
    pass


PROJECT_KEY = os.getenv("DETA_TEST_PROJECT_KEY", "")
BASE_NAME = os.getenv("DETA_TEST_BASE_NAME", "test")


@pytest.fixture()
async def base():
    deta = Deta(PROJECT_KEY)
    yield deta.Base(BASE_NAME)
    await deta.close()
