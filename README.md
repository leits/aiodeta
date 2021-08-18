# aiodeta

Unofficial client for Deta Clound

## Examples

```python
import asyncio
import aiobotocore

DETA_PROJECT_KEY = "xxx_yyy"


async def go():
    db_name = "users"

    # Initialize Deta client
    deta = Deta(DETA_PROJECT_KEY)

    # Initialize Deta Base client
    base = deta.Base(db_name)

    # Create row in Deta Base
    user = {"username": "steve", "active": False}
    resp = await base.insert(user)
    print(resp)
    user_key = resp["key"]

    # Update row by key
    resp = await base.update(user_key, set={"active": True})
    print(resp)

    # Get row by key
    resp = await base.get(user_key)
    print(resp)

    # Delete row by key
    resp = await base.delete(user_key)
    print(resp)

    # Create multiple rows in one request
    users = [
        {"username": "jeff", "active": True},
        {"username": "rob", "active": False},
        {"username": "joe", "active": True}
    ]
    resp = await base.put(users)
    print(resp)

    # Query data
    query = [{"active": True}, {"username?pfx": "j"}]
    result = await base.query(query=query, limit=10)
    print(result)

    # Close connection
    await deta.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(go())
```