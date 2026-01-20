# import chainlit as cl
# from langgraph.types import Command
# from langchain_core.messages import HumanMessage
# from main import app  # Ensure your graph is named 'app' in main.py

# @cl.on_chat_start
# async def on_chat_start():
#     """Initializes the session without requiring an external DB."""
#     # Create a unique thread ID for this browser session
#     thread_id = f"local_session_{cl.user_session.get('id')}"
#     cl.user_session.set("config", {"configurable": {"thread_id": thread_id}})
    
#     await cl.Message(content="🌍 **Travel Architect (Local Mode) Ready.** What's the plan?").send()

# @cl.on_message
# async def on_message(message: cl.Message):
#     config = cl.user_session.get("config")
    
#     # 1. Peek at the current state of the graph
#     state = await app.aget_state(config)
    
#     # 2. Determine if we are Resuming from an Interrupt or starting a new Turn
#     # If the graph is stopped at 'human_interrupter_node', we must use Command(resume=...)
#     if state.next and "human_interrupter_node" in state.next:
#         input_data = Command(resume=message.content)
#     else:
#         input_data = {"messages": [HumanMessage(content=message.content)]}

#     # 3. Execute the Graph
#     # We use stream_mode="updates" to capture when a node finishes its work
#     async for event in app.astream(input_data, config, stream_mode="updates"):
#         for node_name, output in event.items():
#             # You can uncomment the line below to see node transitions in the UI
#             # await cl.Message(content=f"⚙️ Node: {node_name} completed.").send()
#             pass

#     # 4. Final State Analysis & UI Output
#     final_state = await app.aget_state(config)
#     last_msg = final_state.values.get("messages", [])[-1].content if final_state.values.get("messages") else "Error: No response generated."

#     # Check if we stopped because info is missing
#     if final_state.next and "human_interrupter_node" in final_state.next:
#         # Use the 'rewritten_query' which contains your "INCOMPLETE: Missing..." message
#         reason = final_state.values.get("rewritten_query", "Need more info.")
#         await cl.Message(content=f"⚠️ **Clarification Needed:**\n{reason}").send()
#     else:
#         # The task is complete or moved to a standard AI response
#         await cl.Message(content=last_msg).send()
import data_layer  
import chainlit as cl
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from main import app  

@cl.on_chat_start
async def on_chat_start():
    # Setup the thread config for the database
    # This thread_id is what LangGraph uses to look up your trip in Postgres
    thread_id = f"user_{cl.user_session.get('id')}"
    config = {"configurable": {"thread_id": thread_id}}
    cl.user_session.set("config", config)

    await cl.Message(content="🌍 Travel Agent is ready! Where are we going?").send()

@cl.on_message
async def on_message(message: cl.Message):
    config = cl.user_session.get("config")
    state = app.get_state(config)
    
    if state.next and "human_interrupter_node" in state.next:
        input_data = Command(resume=message.content)
    else:
        input_data = {"messages": [HumanMessage(content=message.content)]}

    # We will use this to track if we've already sent a final message
    final_shown = False

    # 3. STREAM THE GRAPH
    # We use app.stream because your PostgresSaver is Synchronous
    for event in app.stream(input_data, config, stream_mode="updates"):
        for node_name, output in event.items():
            
            # --- UPDATE: Tell the user what node is working ---
            if node_name == "researcher_node":
                await cl.Message(content="🔍 *Searching for flights, trains, and hotels...*").send()
            
            elif node_name == "human_interrupter_node":
                if output and "messages" in output:
                    await cl.Message(content=output["messages"][-1].content).send()

            # --- UPDATE: Show the final itinerary ---
            elif node_name == "synthesizer_node":
                if output and "messages" in output:
                    final_answer = output["messages"][-1].content
                    await cl.Message(content=final_answer).send()
                    final_shown = True

    # 4. Fallback: If the loop finishes but nothing was shown
    if not final_shown:
        final_state = app.get_state(config)
        messages = final_state.values.get("messages", [])
        if messages:
            await cl.Message(content=messages[-1].content).send()