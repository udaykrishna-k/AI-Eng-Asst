from langchain_core.messages import HumanMessage


def stream_answer(agent, user_input, config):
    for chunk, metadata in agent.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode="messages",
    ):
        # Only display text from the assistant's main response,
        # not tool-call data or other internal messages.
        if (
            chunk.content
            and metadata.get("langgraph_node") == "model"
            and not chunk.tool_call_chunks
        ):
            if isinstance(chunk.content, str):
                yield chunk.content
            elif isinstance(chunk.content, list):
                for block in chunk.content:
                    if (
                        isinstance(block, dict)
                        and block.get("type") == "text"
                    ):
                        yield block["text"]