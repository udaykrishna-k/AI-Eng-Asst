from typing import Annotated

from langchain.tools import tool
from langgraph.prebuilt import InjectedStore
from langgraph.store.base import BaseStore

from utils import constants


@tool
def save_preference(
    key: str,
    value: str,
    store: Annotated[BaseStore, InjectedStore()],
) -> str:
    """Save a user's preference for future conversations."""

    namespace = ("users", constants.USER_ID, "preferences")

    print(f"DEBUG save: user_id={constants.USER_ID}")
    print(f"DEBUG save: key={key}, value={value}")

    store.put(namespace, key, {"value": value})

    # Immediately read back the saved item.
    saved_item = store.get(namespace, key)

    print(f"DEBUG saved item: {saved_item}")

    if saved_item is None:
        return f"Failed to verify saving preference '{key}'."

    return f"Successfully saved preference '{key}'."

@tool
def get_preference(
    store: Annotated[BaseStore, InjectedStore()],
    key: str = "",
) -> str:
    """Retrieve a saved preference by key, or all preferences if no key is provided."""

    namespace = ("users", constants.USER_ID, "preferences")

    print(f"DEBUG get: user_id={constants.USER_ID}")
    print(f"DEBUG get: namespace={namespace}")
    print(f"DEBUG get: requested key={key!r}")

    if key:
        item = store.get(namespace, key)
        print(f"DEBUG get: item={item}")

        if item is None:
            return f"No saved preference found for '{key}'."

        return item.value["value"]

    items = store.search(namespace)

    print(f"DEBUG get: found {len(items)} preferences")
    for item in items:
        print(f"DEBUG preference: {item.key} = {item.value}")

    if not items:
        return "No saved preferences found."

    return "\n".join(
        f"{item.key}: {item.value['value']}"
        for item in items
    )