import logging

from utils.logging_config import setup_logger

setup_logger()
log = logging.getLogger(__name__)


def load_thread_messages(agent, thread_id):
    """Load saved conversation messages for a thread."""
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    state = agent.get_state(config)

    if not state.values:
        log.info("No saved conversation found for thread_id=%s", thread_id)
        return []

    messages = state.values.get("messages", [])

    ui_messages = []

    for message in messages:
        if message.type == "human":
            ui_messages.append({
                "role": "user",
                "content": message.content,
            })
        elif message.type == "ai" and message.content:
            ui_messages.append({
                "role": "assistant",
                "content": message.content,
            })

    log.info(
        "Loaded %d messages for thread_id=%s",
        len(ui_messages),
        thread_id,
    )

    return ui_messages
