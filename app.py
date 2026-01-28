import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.types import Command
from main import get_async_app
import uuid

@cl.on_chat_start
async def on_chat_start():
    try:
        app = await get_async_app()
        cl.user_session.set("graph_app", app)
        cl.user_session.set("config", {"configurable": {"thread_id": str(uuid.uuid4())}})
        await cl.Message(content="🌍 **Travel Architect 2026 Online.** How can I help?").send()
    except Exception as e:
        await cl.Message(content=f"❌ **Initialization Error:** {str(e)}").send()

@cl.on_message
async def on_message(message: cl.Message):
    app = cl.user_session.get("graph_app")
    config = cl.user_session.get("config")

    if not message.content:
        await cl.Message(content="⚠️ Please enter a message.").send()
        return

    status_msg = cl.Message(content="⚙️ **Thinking...**")
    final_msg = cl.Message(content="")
    reasoning_step = cl.Step(name="Agent Reasoning", type="run")

    reasoning_content = ""
    streaming_started = False
    final_shown = False

    try:
        await status_msg.send()
        state = await app.aget_state(config)

        # Determine if we are resuming from an interrupt or starting fresh
        if state.next:
            input_data = Command(resume=message.content)
        else:
            input_data = {"messages": [HumanMessage(content=message.content)]}

        # We use three modes: updates for node changes, messages for LLM tokens, custom for your research loop
        stream = app.astream(
            input_data,
            config,
            stream_mode=["updates", "messages", "custom"],
            subgraphs=True
        )

        async for chunk in stream:
            # 🟢 DYNAMIC UNPACKING: Handles (mode, content) OR (namespace, mode, content)
            if len(chunk) == 3:
                _, mode, content = chunk
            elif len(chunk) == 2:
                mode, content = chunk
            else:
                continue

            last_chunk_sent = False

            # --- 1. CUSTOM MODE (Captured from StreamWriter in deep_research.py) ---
            if mode == "custom":
                if content.get("node") == "deep_research_node":
                    # Update status message and append to reasoning if "status" is present
                    if "status" in content:
                        status_msg.content = content["status"]
                        await status_msg.update()

                        # Append the status as a header in the reasoning step
                        if not reasoning_step.id:
                            await reasoning_step.send()
                        reasoning_content += f"\n\n### {content['status']}\n"
                        reasoning_step.output = reasoning_content
                        await reasoning_step.update()

                    # Stream to reasoning step if "content" is present
                    elif "content" in content:
                        if not reasoning_step.id:
                            await reasoning_step.send()

                        reasoning_content += content.get("content", "")
                        reasoning_step.output = reasoning_content
                        await reasoning_step.update()

            # --- 2. MESSAGES MODE (Token Streaming) ---
            elif mode == "messages":
                msg_chunk, metadata = content
                curr_node = metadata.get("langgraph_node", "")

                # Start showing the final response when synthesizer starts
                if "synthesizer" in curr_node:
                    if not streaming_started:
                        if status_msg.id: await status_msg.remove()
                        await final_msg.send()
                        streaming_started = True
                        final_shown = True

                    print(msg_chunk)
                    if hasattr(msg_chunk, "content") and isinstance(msg_chunk, AIMessageChunk):
                        await final_msg.stream_token(msg_chunk.content)

            # --- 3. UPDATES MODE (Node Progress & Interrupts) ---
            elif mode == "updates":
                if "__interrupt__" in content:
                    interrupt_val = content["__interrupt__"][0].value
                    if status_msg.id: await status_msg.remove()
                    await cl.Message(content=f"👋 **Need Info:** {interrupt_val}").send()
                    return

                # Get the last node that executed
                node_name = list(content.keys())[-1] if content else ""

                # Dynamic status updates based on node names
                display_names = {
                    "planner_node": "📅 Building Itinerary...",
                    "deep_research_node": "🔍 Deep Researching...",
                    "quick_lookup_node": "⚡ Quick Search...",
                    "rewrite_node": "📝 Refinement...",
                    "human_interruptor": "🛑 Waiting for User..."
                }

                if node_name in display_names:
                    status_msg.content = display_names[node_name]
                    await status_msg.update()

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        if status_msg.id: await status_msg.remove()
        await cl.Message(content=f"⚠️ **Error:** {str(e)}").send()
    finally:
        if final_shown:
            await final_msg.update()
        elif not state.next and not streaming_started:
             # If no streaming happened and no interrupt, ensure status is removed
             if status_msg.id: await status_msg.remove()