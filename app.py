# # # # # import chainlit as cl
# # # # # from langgraph.types import Command
# # # # # from langchain_core.messages import HumanMessage
# # # # # from main import app  # Ensure your graph is named 'app' in main.py

# # # # # @cl.on_chat_start
# # # # # async def on_chat_start():
# # # # #     """Initializes the session without requiring an external DB."""
# # # # #     # Create a unique thread ID for this browser session
# # # # #     thread_id = f"local_session_{cl.user_session.get('id')}"
# # # # #     cl.user_session.set("config", {"configurable": {"thread_id": thread_id}})
    
# # # # #     await cl.Message(content="🌍 **Travel Architect (Local Mode) Ready.** What's the plan?").send()

# # # # # @cl.on_message
# # # # # async def on_message(message: cl.Message):
# # # # #     config = cl.user_session.get("config")
    
# # # # #     # 1. Peek at the current state of the graph
# # # # #     state = await app.aget_state(config)
    
# # # # #     # 2. Determine if we are Resuming from an Interrupt or starting a new Turn
# # # # #     # If the graph is stopped at 'human_interrupter_node', we must use Command(resume=...)
# # # # #     if state.next and "human_interrupter_node" in state.next:
# # # # #         input_data = Command(resume=message.content)
# # # # #     else:
# # # # #         input_data = {"messages": [HumanMessage(content=message.content)]}

# # # # #     # 3. Execute the Graph
# # # # #     # We use stream_mode="updates" to capture when a node finishes its work
# # # # #     async for event in app.astream(input_data, config, stream_mode="updates"):
# # # # #         for node_name, output in event.items():
# # # # #             # You can uncomment the line below to see node transitions in the UI
# # # # #             # await cl.Message(content=f"⚙️ Node: {node_name} completed.").send()
# # # # #             pass

# # # # #     # 4. Final State Analysis & UI Output
# # # # #     final_state = await app.aget_state(config)
# # # # #     last_msg = final_state.values.get("messages", [])[-1].content if final_state.values.get("messages") else "Error: No response generated."

# # # # #     # Check if we stopped because info is missing
# # # # #     if final_state.next and "human_interrupter_node" in final_state.next:
# # # # #         # Use the 'rewritten_query' which contains your "INCOMPLETE: Missing..." message
# # # # #         reason = final_state.values.get("rewritten_query", "Need more info.")
# # # # #         await cl.Message(content=f"⚠️ **Clarification Needed:**\n{reason}").send()
# # # # #     else:
# # # # #         # The task is complete or moved to a standard AI response
# # # # #         await cl.Message(content=last_msg).send()
# # # # import data_layer  
# # # # import chainlit as cl
# # # # from langgraph.types import Command
# # # # from langchain_core.messages import HumanMessage
# # # # from main import app  

# # # # @cl.on_chat_start
# # # # async def on_chat_start():
# # # #     # Setup the thread config for the database
# # # #     # This thread_id is what LangGraph uses to look up your trip in Postgres
# # # #     thread_id = f"user_{cl.user_session.get('id')}"
# # # #     config = {"configurable": {"thread_id": thread_id}}
# # # #     cl.user_session.set("config", config)

# # # #     await cl.Message(content="🌍 Travel Agent is ready! Where are we going?").send()

# # # # # @cl.on_message
# # # # # async def on_message(message: cl.Message):
# # # # #     config = cl.user_session.get("config")
# # # # #     # Get state synchronously
# # # # #     state = app.get_state(config)
    
# # # # #     if state.next and "human_interrupter_node" in state.next:
# # # # #         input_data = Command(resume=message.content)
# # # # #     else:
# # # # #         input_data = {"messages": [HumanMessage(content=message.content)]}

# # # # #     # Use a list to collect the final answer
# # # # #     final_answer = ""

# # # # #     # 3. STREAM THE GRAPH (Sync stream)
# # # # #     for event in app.stream(input_data, config, stream_mode="updates"):
# # # # #         for node_name, output in event.items():
# # # # #             if not output:
# # # # #                 continue
                
# # # # #             # Get the messages from the current node's output
# # # # #             node_messages = output.get("messages", [])
# # # # #             if node_messages:
# # # # #                 last_msg_content = node_messages[-1].content
                
# # # # #                 # If it's the interrupter or the synthesizer, we want to show it
# # # # #                 if node_name in ["human_interrupter_node", "synthesizer_node"]:
# # # # #                     final_answer = last_msg_content

# # # # #     # 4. Send the result to the UI
# # # # #     if final_answer:
# # # # #         await cl.Message(content=final_answer).send()
# # # # #     else:
# # # # #         # Fallback: get the last message from state
# # # # #         final_state = app.get_state(config)
# # # # #         messages = final_state.values.get("messages", [])
# # # # #         if messages:
# # # # #             await cl.Message(content=messages[-1].content).send()
# # # # @cl.on_message
# # # # async def on_message(message: cl.Message):
# # # #     config = cl.user_session.get("config")
# # # #     state = app.get_state(config)
    
# # # #     # 1. Handle Resuming vs starting New
# # # #     if state.next and "human_interrupter_node" in state.next:
# # # #         # We are resuming from the interrupt with the user's answer
# # # #         input_data = Command(resume=message.content)
# # # #     else:
# # # #         # Starting a new request
# # # #         input_data = {"messages": [HumanMessage(content=message.content)]}

# # # #     final_shown = False

# # # #     # 2. STREAM THE GRAPH
# # # #     for event in app.stream(input_data, config, stream_mode="updates"):
# # # #         for node_name, output in event.items():
# # # #             if not output:
# # # #                 continue
                
# # # #             # --- UPDATE: Handle the Clarification Message ---
# # # #             if node_name == "human_interrupter_node":
# # # #                 # Check if your node stores the reason in 'messages' or 'rewritten_query'
# # # #                 interrupt_msg = ""
# # # #                 if "messages" in output:
# # # #                     interrupt_msg = output["messages"][-1].content
# # # #                 elif "rewritten_query" in output:
# # # #                     interrupt_msg = output[ "rewritten_query"]
                
# # # #                 if interrupt_msg:
# # # #                     # Create a message and stream it for a better UI feel
# # # #                     msg = cl.Message(content="")
# # # #                     await msg.send()
# # # #                     for token in interrupt_msg.split(" "):
# # # #                         await msg.stream_token(token + " ")
# # # #                     await msg.update()
# # # #                     final_shown = True

# # # #             # --- Handle the Final Answer ---
# # # #             elif node_name == "synthesizer_node":
# # # #                 node_messages = output.get("messages", [])
# # # #                 if node_messages:
# # # #                     final_answer = node_messages[-1].content
# # # #                     msg = cl.Message(content="")
# # # #                     await msg.send()
# # # #                     for token in final_answer.split(" "):
# # # #                         await msg.stream_token(token + " ")
# # # #                     await msg.update()
# # # #                     final_shown = True

# # # #     # 3. Fallback: Show last message if loop finished without streaming
# # # #     if not final_shown:
# # # #         final_state = app.get_state(config)
# # # #         messages = final_state.values.get("messages", [])
# # # #         if messages:
# # # #             await cl.Message(content=messages[-1].content).send()
# import chainlit as cl
# from langgraph.types import Command
# from langchain_core.messages import HumanMessage
# from main import app as graph_app  # Your LangGraph instance
# import uuid

# @cl.on_chat_start
# async def on_chat_start():
#     # Similar to Mission ID in your Streamlit code
#     mission_id = str(uuid.uuid4())
#     cl.user_session.set("mission_id", mission_id)
#     cl.user_session.set("task_log", [])
    
#     # Initialize UI Settings (Deep vs Fast mode could be a header or button in Chainlit)
#     await cl.Message(content="🌀 **Deep Travel Research Agent Ready.** What's the plan?").send()


# @cl.on_message
# async def on_message(message: cl.Message):
#     # 1. Retrieve configuration and session data
#     config = cl.user_session.get("config")
#     task_log = cl.user_session.get("task_log", [])
    
#     # 2. Bridge Sync LangGraph with Async Chainlit
#     # We use cl.make_async to prevent the NotImplementedError from the Postgres checkpointer
#     state = await cl.make_async(graph_app.get_state)(config)
    
#     # 3. Determine if we are Resuming from an Interrupt or starting fresh
#     if state.next and "human_interrupter_node" in state.next:
#         # User is answering a clarification question
#         input_data = Command(resume=message.content)
#     else:
#         # New request (similar to your Streamlit 'inputs')
#         input_data = {
#             "messages": [HumanMessage(content=message.content)],
#             "user_query": message.content,
#             "mode": "fast"  # You can pull this from a Chainlit Action/Toggle if desired
#         }

#     # 4. UI Placeholders
#     # 'status_msg' acts like your Streamlit status_area
#     status_msg = cl.Message(content="🌀 **Travel Agent starting research...**")
#     await status_msg.send()
    
#     final_shown = False

#     # 5. STREAM THE GRAPH (Synchronous stream wrapped for Async)
#     # We use cl.make_async to run the generator without blocking
#     async_stream = cl.make_async(graph_app.stream)
    
#     for event in await async_stream(input_data, config, stream_mode="updates"):
#         for node_name, output in event.items():
#             if not output:
#                 continue

#             # --- A. Progress Tracking (Streamlit task_log logic) ---
#             current_task = output.get("active_task_description")
#             if current_task and str(current_task).lower() != "none":
#                 if current_task not in task_log:
#                     task_log.append(current_task)
#                     # Update the on-screen status (like st.empty() in Streamlit)
#                     status_msg.content = f"🔎 **Agent is researching:** {current_task}"
#                     await status_msg.update()

#             # --- B. Handle Human Interrupts (Clarification) ---
#             if node_name == "human_interrupter_node":
#                 interrupt_msg = output.get("messages")[-1].content if output.get("messages") else "Need more info."
#                 await cl.Message(content=f"⚠️ **Action Required:**\n{interrupt_msg}").send()
#                 final_shown = True

#             # --- C. Handle Final Report (Synthesizer) ---
#             elif node_name == "synthesizer_node":
#                 node_messages = output.get("messages", [])
#                 if node_messages:
#                     report_content = node_messages[-1].content
                    
#                     # Create a "Typewriter" streaming effect for the final report
#                     report_msg = cl.Message(content="")
#                     await report_msg.send()
#                     for word in report_content.split(" "):
#                         await report_msg.stream_token(word + " ")
#                     await report_msg.update()
#                     final_shown = True

#     # 6. Fallback & Cleanup
#     cl.user_session.set("task_log", task_log)
    
#     if not final_shown:
#         # Final check of state if loop finished without a direct message
#         final_state = await cl.make_async(graph_app.get_state)(config)
#         msgs = final_state.values.get("messages", [])
#         if msgs:
#             await cl.Message(content=msgs[-1].content).send()

#     # 7. Show research history in a collapsible Step (Professional Finish)
#     if task_log:
#         async with cl.Step(name="Research History") as step:
#             step.output = "\n".join([f"✅ {task}" for task in task_log])
# # import chainlit as cl
# # import uuid
# # import asyncio
# # from langchain_core.messages import HumanMessage
# # from langgraph.types import Command
# # from main import get_async_app 

# # @cl.on_chat_start
# # async def on_chat_start():
# #     try:
# #         app = await get_async_app()
# #         cl.user_session.set("graph_app", app)
        
# #         thread_id = str(uuid.uuid4())
# #         # Note: Added 'user' to config to support our history filtering logic
# #         user = cl.user_session.get("user")
# #         config = {"configurable": {"thread_id": thread_id, "user": user.identifier}}
        
# #         cl.user_session.set("config", config)
# #         cl.user_session.set("task_log", [])
        
# #         await cl.Message(content="🌍 **Travel Architect Online.** Ready to plan your journey!").send()
# #     except Exception as e:
# #         await cl.Message(content=f"❌ Initialization Error: {str(e)}").send()

# # @cl.on_message
# # async def on_message(message: cl.Message):
# #     app = cl.user_session.get("graph_app")
# #     config = cl.user_session.get("config")
# #     task_log = cl.user_session.get("task_log", [])

# #     state = await app.aget_state(config)
    
# #     # Check if we are resuming from an interrupt
# #     if state.next and "human_interrupter_node" in state.next:
# #         input_data = Command(resume=message.content)
# #     else:
# #         input_data = {"messages": [HumanMessage(content=message.content)]}

# #     status_msg = cl.Message(content="⚙️ **Thinking...**")
# #     await status_msg.send()
    
# #     final_msg = cl.Message(content="")
# #     final_shown = False
# #     interrupted = False

# #     try:
# #         async for mode, content in app.astream(
# #             input_data, 
# #             config, 
# #             stream_mode=["updates", "messages"]
# #         ):
# #             # --- 🟢 MODE: UPDATES ---
# #             if mode == "updates":
# #                 node_name = list(content.keys())[0]
# #                 output = content[node_name]
                
# #                 if not output or not isinstance(output, dict):
# #                     continue
                
# #                 # Update UI Status
# #                 labels = {
# #                     "rewrite_node": "📝 **Refining your request...**",
# #                     "planner_node": "📅 **Drafting itinerary...**",
# #                     "deep_research_node": "🔍 **Conducting research...**",
# #                     "quick_lookup_node": "⚡ **Checking facts...**"
# #                 }
# #                 if node_name in labels:
# #                     status_msg.content = labels[node_name]
# #                     await status_msg.update()

# #                 # Track tasks for the history log
# #                 current_task = output.get("active_task_description")
# #                 if current_task and str(current_task).lower() != "none":
# #                     if current_task not in task_log:
# #                         task_log.append(current_task)

# #                 # HANDLE INTERRUPTS
# #                 if node_name == "human_interrupter_node":
# #                     await status_msg.remove()
                    
# #                     interrupt_text = ""
# #                     if "messages" in output and output["messages"]:
# #                         interrupt_text = output["messages"][-1].content
# #                     elif "rewritten_query" in output:
# #                         interrupt_text = output["rewritten_query"]
                    
# #                     if interrupt_text:
# #                         await cl.Message(
# #                             content=f"👋 **Wait! I need a few more details:**\n\n{interrupt_text}"
# #                         ).send()
                    
# #                     final_shown = True
# #                     interrupted = True
# #                     break # Critical: Stop the generator loop

# #             # --- 🔵 MODE: MESSAGES (Streaming) ---
# #             elif mode == "messages":
# #                 chunk, metadata = content
                
# #                 if metadata.get("langgraph_node") == "synthesizer_node":
# #                     if not final_msg.content:
# #                         if status_msg.id: await status_msg.remove()
# #                         await final_msg.send()
                    
# #                     await final_msg.stream_token(chunk.content)
# #                     final_shown = True

# #         # --- AFTER THE LOOP ---
# #         if interrupted:
# #             return # Exit safely

# #         if final_msg.content:
# #             await final_msg.update()
        
# #         cl.user_session.set("task_log", task_log)

# #         # Fallback if no streaming occurred
# #         if not final_shown:
# #             final_state = await app.aget_state(config)
# #             msgs = final_state.values.get("messages", [])
# #             if msgs:
# #                 if status_msg.id: await status_msg.remove()
# #                 await cl.Message(content=msgs[-1].content).send()

# #         # Collapsible Step for Research Log
# #         if task_log:
# #             async with cl.Step(name="Research History") as step:
# #                 step.output = "\n".join([f"✅ {task}" for task in task_log])

# #     except Exception as e:
# #         if status_msg.id: await status_msg.remove()
# #         await cl.Message(content=f"🚨 Error: {str(e)}").send()
# #         await cl.Message(content=f"🚨 Error during execution: {str(e)}").send()
# # # import chainlit as cl
# # # import uuid
# # # from langchain_core.messages import HumanMessage
# # # from langgraph.types import Command
# # # from main import get_async_app  # Ensure this returns the compiled graph

# # # # --- 1. CHAT START: Initialize Graph and Session ---
# # # @cl.on_chat_start
# # # async def on_chat_start():
# # #     try:
# # #         # Initialize the async graph (and Postgres connection)
# # #         app = await get_async_app()
# # #         cl.user_session.set("graph_app", app)
        
# #         # Create a unique thread_id for this conversation
# #         thread_id = str(uuid.uuid4())
# #         config = {"configurable": {"thread_id": thread_id}}
# #         cl.user_session.set("config", config)
        
# #         # Initialize task log for progress tracking
# #         cl.user_session.set("task_log", [])
        
# #         await cl.Message(content="🌍 **Travel Architect Online.** Ready to plan your journey!").send()
# #     except Exception as e:
# #         await cl.Message(content=f"❌ Initialization Error: {str(e)}").send()

# # # --- 2. ON MESSAGE: Handle User Input and Streaming ---
# # @cl.on_message
# # async def on_message(message: cl.Message):
# #     # Retrieve app and config from session
# #     app = cl.user_session.get("graph_app")
# #     config = cl.user_session.get("config")
# #     task_log = cl.user_session.get("task_log", [])

# #     # SAFETY: Check if app exists
# #     if not app:
# #         app = await get_async_app()
# #         cl.user_session.set("graph_app", app)

# #     # 1. Check state to see if we are RESUMING an interrupt
# #     state = await app.aget_state(config)
    
# #     if state.next:
# #         # If there is a 'next' node, the graph is paused. Resume it!
# #         input_data = Command(resume=message.content)
# #     else:
# #         # Starting a fresh turn
# #         input_data = {"messages": [HumanMessage(content=message.content)]}

# #     # UI Placeholders
# #     status_msg = cl.Message(content="⚙️ **Thinking...**")
# #     await status_msg.send()
    
# #     final_msg = cl.Message(content="")
# #     final_shown = False

# #     try:
# #         # 2. STREAM THE GRAPH
# #         async for mode, content in app.astream(
# #             input_data, 
# #             config, 
# #             stream_mode=["updates", "messages"]
# #         ):
# #             # 🟢 HANDLE INTERRUPTS (The "Missing Info" prompt)
# #             if mode == "updates" and "__interrupt__" in content:
# #                 if status_msg.id: await status_msg.remove()
                
# #                 interrupt_data = content["__interrupt__"]
# #                 # Payload from your interrupt() call in human_interrupter_node
# #                 question = interrupt_data[0].value if interrupt_data else "I need more info."
                
# #                 await cl.Message(content=f"👋 **Wait! I need a few more details:**\n\n{question}").send()
# #                 final_shown = True
# #                 return # Stop and wait for user reply

# #             # 🔵 HANDLE NODE UPDATES (Progress Status)
# #             if mode == "updates":
# #                 node_name = list(content.keys())[0]
# #                 output = content[node_name]
                
# #                 if not output or not isinstance(output, dict):
# #                     continue

# #                 # Update Status Labels
# #                 labels = {
# #                     "rewrite_node": "📝 **Analyzing request...**",
# #                     "planner_node": "📅 **Drafting plan...**",
# #                     "deep_research_node": "🔍 **Deep searching...**",
# #                     "quick_lookup_node": "⚡ **Checking facts...**"
# #                 }
# #                 if node_name in labels:
# #                     status_msg.content = labels[node_name]
# #                     await status_msg.update()

# #                 # Update Task Log
# #                 current_task = output.get("active_task_description")
# #                 if current_task and str(current_task).lower() != "none":
# #                     if current_task not in task_log:
# #                         task_log.append(current_task)

# #             # 🔵 HANDLE TOKEN STREAMING (Synthesizer Output)
# #             elif mode == "messages":
# #                 chunk, metadata = content
# #                 if metadata.get("langgraph_node") == "synthesizer_node":
# #                     if not final_msg.content:
# #                         if status_msg.id: await status_msg.remove()
# #                         await final_msg.send()
                    
# #                     await final_msg.stream_token(chunk.content)
# #                     final_shown = True

# #         # 3. FINAL UI CLEANUP
# #         if final_msg.content:
# #             await final_msg.update()
        
# #         cl.user_session.set("task_log", task_log)

# #         # Fallback if nothing was shown (e.g. state restoration)
# #         if not final_shown:
# #             final_state = await app.aget_state(config)
# #             msgs = final_state.values.get("messages", [])
# #             if msgs:
# #                 if status_msg.id: await status_msg.remove()
# #                 await cl.Message(content=msgs[-1].content).send()

# #         # Show Research History
# #         if task_log:
# #             async with cl.Step(name="Research History") as step:
# #                 step.output = "\n".join([f"✅ {task}" for task in task_log])

# #     except Exception as e:
# #         if status_msg.id: await status_msg.remove()
# #         await cl.Message(content=f"🚨 Error: {str(e)}").send()
# import chainlit as cl
# import uuid
# import psycopg
# import bcrypt
# from psycopg.rows import dict_row
# from langchain_core.messages import HumanMessage
# from langgraph.types import Command
# from main import get_async_app 

# # --- CONFIGURATION ---
# DB_URI = "postgresql://tarinijain@localhost:5432/travel_db"

# # --- 1. SECURE AUTH & SIGN-UP ---
# @cl.password_auth_callback
# async def auth_callback(username, password):
#     try:
#         async with await psycopg.AsyncConnection.connect(DB_URI, row_factory=dict_row) as conn:
#             async with conn.cursor() as cur:
#                 # Look for existing user
#                 await cur.execute("SELECT * FROM app_users WHERE username = %s", (username,))
#                 user = await cur.fetchone()

#                 password_bytes = password.encode('utf-8')

#                 if user:
#                     # LOGIN: Verify existing password
#                     stored_hash = user["password_hash"].encode('utf-8')
#                     if bcrypt.checkpw(password_bytes, stored_hash):
#                         return cl.User(identifier=username, metadata={"new_user": False})
#                 else:
#                     # SIGN-UP: User doesn't exist, create them automatically
#                     salt = bcrypt.gensalt()
#                     hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
                    
#                     await cur.execute(
#                         "INSERT INTO app_users (username, password_hash) VALUES (%s, %s)",
#                         (username, hashed)
#                     )
#                     await conn.commit()
#                     return cl.User(identifier=username, metadata={"new_user": True})
                    
#                 print(f"❌ Login failed for {username}")
#     except Exception as e:
#         print(f"🚨 Auth/Sign-up Error: {e}")
#     return None

# # # --- 2. HISTORY UTILITY ---
# # async def fetch_user_history(username: str):
# #     """Fetches unique thread IDs associated with this user."""
# #     try:
# #         async with await psycopg.AsyncConnection.connect(DB_URI, row_factory=dict_row) as conn:
# #             async with conn.cursor() as cur:
# #                 # Note: This assumes your checkpointer metadata stores the user identifier
# #                 await cur.execute(
# #                     "SELECT DISTINCT thread_id FROM checkpoints WHERE metadata->>'user' = %s ORDER BY thread_id DESC LIMIT 8",
# #                     (username,)
# #                 )
# #                 rows = await cur.fetchall()
# #                 return [r["thread_id"] for r in rows]
# #     except Exception as e:
# #         print(f"History Fetch Error: {e}")
# #         return []

# # # --- 3. CHAT START ---
# # @cl.on_chat_start
# # async def on_chat_start():
# #     try:
# #         app = await get_async_app()
# #         cl.user_session.set("graph_app", app)
        
# #         user = cl.user_session.get("user")
# #         is_new = user.metadata.get("new_user", False)

# #         # Config with user-specific metadata for the checkpointer
# #         thread_id = str(uuid.uuid4())
# #         config = {
# #             "configurable": {
# #                 "thread_id": thread_id,
# #                 "user": user.identifier  # This helps filter history later
# #             }
# #         }
# #         cl.user_session.set("config", config)
# #         cl.user_session.set("task_log", [])

# #         # Build Sidebar History
# #         history = await fetch_user_history(user.identifier)
# #         actions = [
# #             cl.Action(name="load_thread", value=tid, label=f"Trip: {tid[:8]}")
# #             for tid in history
# #         ]

# #         welcome_text = (
# #             f"🎊 **Welcome to the club, {user.identifier}!** Your account is ready." 
# #             if is_new else 
# #             f"👋 **Welcome back, {user.identifier}!**"
# #         )

# #         await cl.Message(
# #             content=f"{welcome_text} Your past travel research is in the sidebar. To start fresh, just type your destination below.",
# #             actions=actions
# #         ).send()
        
# #     except Exception as e:
# #         await cl.Message(content=f"❌ Initialization Error: {str(e)}").send()

# # # --- 4. ACTION CALLBACK (Switching History) ---
# # @cl.action_callback("load_thread")
# # async def on_action(action):
# #     user = cl.user_session.get("user")
# #     new_config = {
# #         "configurable": {
# #             "thread_id": action.value,
# #             "user": user.identifier
# #         }
# #     }
# #     cl.user_session.set("config", new_config)
# #     cl.user_session.set("task_log", [])
    
# #     await cl.Message(content=f"🔄 **Trip Loaded.** Resuming session `{action.value[:8]}`...").send()

# # # --- 5. ON MESSAGE ---
# # @cl.on_message
# # async def on_message(message: cl.Message):
# #     app = cl.user_session.get("graph_app")
# #     config = cl.user_session.get("config")
# #     task_log = cl.user_session.get("task_log", [])

# #     if not app:
# #         app = await get_async_app()
# #         cl.user_session.set("graph_app", app)

# #     state = await app.aget_state(config)
    
# #     # Handle Resume (Interrupts) vs New Turn
# #     if state.next:
# #         input_data = Command(resume=message.content)
# #     else:
# #         input_data = {"messages": [HumanMessage(content=message.content)]}

# #     status_msg = cl.Message(content="⚙️ **Thinking...**")
# #     await status_msg.send()
    
# #     final_msg = cl.Message(content="")
# #     final_shown = False

# #     try:
# #         async for mode, content in app.astream(
# #             input_data, config, stream_mode=["updates", "messages"]
# #         ):
# #             # CATCH INTERRUPTS
# #             if mode == "updates" and "__interrupt__" in content:
# #                 if status_msg.id: await status_msg.remove()
# #                 interrupt_data = content["__interrupt__"]
# #                 question = interrupt_data[0].value if interrupt_data else "Need more info."
# #                 await cl.Message(content=f"👋 **Wait! I need a few more details:**\n\n{question}").send()
# #                 final_shown = True
# #                 return 

# #             # NODE UPDATES (Status labels)
# #             if mode == "updates":
# #                 node_name = list(content.keys())[0]
# #                 output = content[node_name]
# #                 if not output or not isinstance(output, dict): continue

# #                 labels = {
# #                     "rewrite_node": "📝 **Analyzing...**",
# #                     "planner_node": "📅 **Planning...**",
# #                     "deep_research_node": "🔍 **Researching...**",
# #                     "quick_lookup_node": "⚡ **Checking...**"
# #                 }
# #                 if node_name in labels:
# #                     status_msg.content = labels[node_name]
# #                     await status_msg.update()

# #                 current_task = output.get("active_task_description")
# #                 if current_task and str(current_task).lower() != "none":
# #                     if current_task not in task_log:
# #                         task_log.append(current_task)

# #             # TOKEN STREAMING
# #             elif mode == "messages":
# #                 chunk, metadata = content
# #                 if metadata.get("langgraph_node") == "synthesizer_node":
# #                     if not final_msg.content:
# #                         if status_msg.id: await status_msg.remove()
# #                         await final_msg.send()
# #                     await final_msg.stream_token(chunk.content)
# #                     final_shown = True

# #         if final_msg.content:
# #             await final_msg.update()
        
# #         cl.user_session.set("task_log", task_log)

# #         # Fallback for state recovery
# #         if not final_shown:
# #             final_state = await app.aget_state(config)
# #             msgs = final_state.values.get("messages", [])
# #             if msgs:
# #                 if status_msg.id: await status_msg.remove()
# #                 await cl.Message(content=msgs[-1].content).send()

# #         # Display research history steps
# #         if task_log:
# #             async with cl.Step(name="Research History") as step:
# #                 step.output = "\n".join([f"✅ {task}" for task in task_log])

# #     except Exception as e:
# #         if status_msg.id: await status_msg.remove()
# #         await cl.Message(content=f"🚨 Error: {str(e)}").send()
import chainlit as cl
import uuid
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from main import get_async_app 

@cl.on_chat_start
async def on_chat_start():
    try:
        # 1. Initialize the Graph
        app = await get_async_app()
        cl.user_session.set("graph_app", app)
        
        # 2. Get User with Safety Guard
        user = cl.user_session.get("user")
        
        # Check if user is None (happens if auth isn't finished or session is stale)
        if not user:
            # Fallback to a guest ID or show a friendly error
            username = "Guest"
        else:
            username = user.identifier

        # 3. Setup Persistence Config
        thread_id = str(uuid.uuid4())
        config = {
            "configurable": {
                "thread_id": thread_id, 
                "user": username  # Using our safe username variable
            }
        }
        
        cl.user_session.set("config", config)
        cl.user_session.set("task_log", [])
        
        await cl.Message(content=f"🌍 **Welcome, {username}!** Ready to plan your journey!").send()
        
    except Exception as e:
        print(f"Detailed Init Error: {e}")
        await cl.Message(content=f"❌ Initialization Error: {str(e)}").send()

@cl.on_message
async def on_message(message: cl.Message):
    app = cl.user_session.get("graph_app")
    config = cl.user_session.get("config")
    task_log = cl.user_session.get("task_log", [])

    state = await app.aget_state(config)
    print(state)
    
    # Check if we are resuming or starting new
    if state.next and "human_interrupter_node" in state.next:
        input_data = Command(resume=message.content)
    else:
        input_data = {"messages": [HumanMessage(content=message.content)]}

    status_msg = cl.Message(content="⚙️ **Thinking...**")
    await status_msg.send()
    
    final_msg = cl.Message(content="")
    final_shown = False
    interrupt_content = None

    # --- THE FIX: MANAGE THE STREAM LIFECYCLE ---
    stream = app.astream(input_data, config, stream_mode=["updates", "messages"])

    try:
        async for mode, content in stream:
            if mode == "updates":
                node_name = list(content.keys())[0]
                output = content[node_name]
                
                if not output or not isinstance(output, dict):
                    continue
                
                # 1. Handle Interrupts (Store content and BREAK)
                if node_name == "human_interrupter_node":
                    if "messages" in output and output["messages"]:
                        interrupt_content = output["messages"][-1].content
                    elif "rewritten_query" in output:
                        interrupt_content = output["rewritten_query"]
                    break # Stop the generator naturally

                # 2. Update status labels
                labels = {
                    "rewrite_node": "📝 Refining...",
                    "planner_node": "📅 Planning...",
                    "deep_research_node": "🔍 Researching..."
                }
                if node_name in labels:
                    status_msg.content = labels[node_name]
                    await status_msg.update()

                # 3. Task logging
                task = output.get("active_task_description")
                if task and str(task).lower() != "none" and task not in task_log:
                    task_log.append(task)

            elif mode == "messages":
                chunk, metadata = content
                if metadata.get("langgraph_node") == "synthesizer_node":
                    if not final_msg.content:
                        if status_msg.id: await status_msg.remove()
                        await final_msg.send()
                    await final_msg.stream_token(chunk.content)
                    final_shown = True
    finally:
        # EXTREMELY IMPORTANT: Force the generator to close
        await stream.aclose()

    # --- FINAL UI UPDATES (After stream is closed) ---
    if interrupt_content:
        if status_msg.id: await status_msg.remove()
        await cl.Message(content=f"👋 **Wait! I need details:**\n\n{interrupt_content}").send()
        return

    if final_msg.content:
        await final_msg.update()
    
    if not final_shown:
        final_state = await app.aget_state(config)
        msgs = final_state.values.get("messages", [])
        if msgs:
            if status_msg.id: await status_msg.remove()
            await cl.Message(content=msgs[-1].content).send()

    # Show history log
    cl.user_session.set("task_log", task_log)
    if task_log:
        async with cl.Step(name="Research History") as step:
            step.output = "\n".join([f"✅ {t}" for t in task_log])