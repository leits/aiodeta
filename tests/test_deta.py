import pytest

from aiodeta import Deta

pytestmark = pytest.mark.asyncio


async def test_init():
    deta = Deta("id_key")
    assert deta.project_id == "id"
    assert deta.project_key == "id_key"


async def test_init_bad_key():
    with pytest.raises(ValueError, match="Bad project key provided"):
        Deta("key-without-underscore")
