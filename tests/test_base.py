import os
import uuid

import pytest

from aiodeta import Deta

try:
    from dotenv import load_dotenv

    load_dotenv()
except:
    pass


PROJECT_KEY = os.getenv("DETA_TEST_PROJECT_KEY", "")
BASE_NAME = os.getenv("DETA_TEST_BASE_NAME", "test")

pytestmark = pytest.mark.asyncio


@pytest.fixture()
async def base():
    deta = Deta(PROJECT_KEY)
    yield deta.Base(BASE_NAME)
    await deta.close()


@pytest.fixture
async def make_items(base):
    async def _make_items(items: list):
        result = await base.put(items)
        return result["processed"]["items"]

    yield _make_items


@pytest.fixture()
async def item(make_items):
    data = [
        {
            "username": "jimmy",
            "profile": {"age": 32, "active": False, "hometown": "pittsburgh"},
            "on_mobile": False,
            "likes": ["anime"],
            "purchases": 1,
        }
    ]
    items = await make_items(data)
    yield items[0]


async def test_insert(base):
    payload = {"value": "row"}
    result = await base.insert(payload)
    assert "key" in result
    result.pop("key")
    assert result == payload


async def test_put(base):
    payload = [{"value": "row1"}, {"value": "row2"}]
    result = await base.put(payload)
    assert list(result.keys()) == ["processed"]
    processed_items = result["processed"]["items"]
    for row in processed_items:
        assert "key" in row
        row.pop("key")
    assert processed_items == payload


async def test_get(base, item):
    result = await base.get(item["key"])
    assert result == item


async def test_delete(base, item):
    result = await base.delete(item["key"])
    assert result == None


async def test_update(base, item):
    payload = {
        "set": {
            "profile.age": 33,
            "profile.active": True,
            "profile.email": "jimmy@deta.sh",
        },
        "increment": {"purchases": 2},
        "append": {"likes": ["ramen"]},
        "delete": ["profile.hometown", "on_mobile"],
    }

    result = await base.update(item["key"], **payload)
    assert "key" in result
    result.pop("key")
    assert result == payload


async def test_query(base, make_items):
    test_id = uuid.uuid4().hex
    data = [
        {
            "username": "jimmy",
            "test_id": test_id,
            "age": 32,
            "active": False,
        },
        {
            "username": "tommy",
            "test_id": test_id,
            "age": 25,
            "active": True,
        },
        {
            "username": "lilly",
            "test_id": test_id,
            "age": 25,
            "active": False,
        },
        {
            "username": "ted",
            "test_id": test_id,
            "age": 45,
            "active": True,
        },
    ]
    await make_items(data)

    filtered_usernames = {"tommy", "lilly", "ted"}
    query = [
        {"test_id": test_id, "active": True},
        {"test_id": test_id, "age?lt": 30},
    ]

    result = await base.query(query=query, limit=2)

    assert "items" in result
    assert "paging" in result
    assert result["paging"]["size"] == 2

    result_usernames = {item["username"] for item in result["items"]}
    assert result_usernames.difference(filtered_usernames) == set()

    result = await base.query(query=query, limit=2, last=result["paging"]["last"])

    assert "items" in result
    assert "paging" in result
    assert not "last" in result["paging"]

    result_usernames = {item["username"] for item in result["items"]}
    assert result_usernames.difference(filtered_usernames) == set()
