from typing import List

import aiohttp


class Deta:
    def __init__(self, project_key: str, project_id: str = None):
        if not "_" in project_key:
            raise ValueError("Bad project key provided")

        if not project_id:
            project_id = project_key.split("_")[0]

        self.project_key = project_key
        self.project_id = project_id
        self._session = aiohttp.ClientSession(
            headers={
                "Content-type": "application/json",
                "X-API-Key": project_key,
            },
        )

    async def close(self) -> None:
        await self._session.close()

    def Base(self, name: str, host: str = None) -> "_Base":
        host = host or "database.deta.sh"
        base_url = f"https://{host}/v1/{self.project_id}/{name}"
        return _Base(self._session, base_url)


class _Base:
    def __init__(self, session: aiohttp.ClientSession, base_url: str):
        self._session = session
        self._base_url = base_url

    async def insert(self, data: dict):
        async with self._session.post(
            f"{self._base_url}/items", json={"item": data}
        ) as resp:
            return await resp.json()

    async def put(self, items: List[dict]):
        if len(items) > 25:
            raise ValueError("We can't put more than 25 items at a time.")
        async with self._session.put(
            f"{self._base_url}/items", json={"items": items}
        ) as resp:
            return await resp.json()

    async def update(
        self,
        key: str,
        set: dict = None,
        increment: dict = None,
        append: dict = None,
        prepend: dict = None,
        delete: list = None,
    ):
        payload = {}
        if set:
            payload["set"] = set
        if increment:
            payload["increment"] = increment
        if append:
            payload["append"] = append
        if prepend:
            payload["prepend"] = prepend
        if delete:
            payload["delete"] = delete

        if not payload:
            raise ValueError("Provide at least one update action.")

        async with self._session.patch(
            f"{self._base_url}/items/{key}", json=payload
        ) as resp:
            return await resp.json()

    async def get(self, key: str):
        async with self._session.get(f"{self._base_url}/items/{key}") as resp:
            return await resp.json()

    async def delete(self, key: str):
        async with self._session.delete(f"{self._base_url}/items/{key}"):
            return

    async def query(self, query: list = None, limit: int = None, last: str = None):
        payload = {}
        if query:
            payload["query"] = query
        if limit:
            payload["limit"] = limit
        if last:
            payload["last"] = last
        async with self._session.post(f"{self._base_url}/query", json=payload) as resp:
            return await resp.json()
