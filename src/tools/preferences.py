import logging
from typing import Annotated

from langchain.tools import tool
from langgraph.prebuilt import InjectedStore
from langgraph.store.base import BaseStore

from utils import constants


log = logging.getLogger(__name__)


@tool
def save_preference(
    key: str,
    value: str,
    store: Annotated[BaseStore, InjectedStore()],
) -> str:
    """Save a user's preference for future conversations."""

    namespace = ("users", constants.USER_ID, "preferences")

    log.info("Saving user preference")
    log.debug(
        "Save preference metadata: user_id=%s, key=%s",
        constants.USER_ID,
        key,
    )

    try:
        store.put(namespace, key, {"value": value})

        # Verify that the preference was saved.
        saved_item = store.get(namespace, key)

        if saved_item is None:
            log.error("Preference save verification failed for key=%s", key)
            return f"Failed to verify saving preference '{key}'."

        log.info("User preference saved and verified successfully")
        return f"Successfully saved preference '{key}'."

    except Exception:
        log.exception("Failed to save user preference")
        raise


@tool
def get_preference(
    store: Annotated[BaseStore, InjectedStore()],
    key: str = "",
) -> str:
    """Retrieve a saved preference by key, or all preferences if no key is provided."""

    namespace = ("users", constants.USER_ID, "preferences")

    log.info("Retrieving user preference")
    log.debug(
        "Get preference metadata: user_id=%s, lookup_type=%s",
        constants.USER_ID,
        "specific key" if key else "all preferences",
    )

    try:
        if key:
            item = store.get(namespace, key)

            if item is None:
                log.warning("No saved preference found for key=%s", key)
                return f"No saved preference found for '{key}'."

            log.info("Preference retrieved successfully")
            return item.value["value"]

        items = store.search(namespace)

        log.debug("Found %d saved preferences", len(items))

        if not items:
            log.info("No saved preferences exist")
            return "No saved preferences found."

        log.info("Retrieved all saved preferences successfully")

        return "\n".join(
            f"{item.key}: {item.value['value']}"
            for item in items
        )

    except Exception:
        log.exception("Failed to retrieve user preference")
        raise
