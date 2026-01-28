# # # import os
# # # from langgraph.graph import StateGraph, START, END
# # # from langgraph.checkpoint.memory import MemorySaver
# # # from langchain_core.messages import HumanMessage
# # # # 1. Import your modular state and nodes
# # # from state import AgentState
# # # from nodes.rewrite import rewrite_node
# # # from nodes.planner import planner_node
# # # from nodes.deep_research import deep_research_node
# # # from nodes.quick_lookup import quick_lookup_node
# # # from nodes.synthesizer import synthesizer_node
# # # from nodes.human_interruptor import human_interrupter_node # Your file
# # # from typing import Literal
# # # # 2. Setup Persistence (Necessary for the 'interrupt' function to work)
# # # memory = MemorySaver()

# # # # 3. Initialize the Graph
# # # builder = StateGraph(AgentState)

# # # # 4. Add Nodes
# # # # Note: Ensure the node names used in Command(goto="...") match these strings exactly.
# # # # --- 1. Define ONE Clean Router ---
# # # def master_router(state: AgentState) -> Literal["human_interrupter_node", "planner_node", "quick_lookup_node"]:
# # #     # CRITICAL: Always check completeness FIRST
# # #     if state.get("is_incomplete", False):
# # #         print("--- ROUTER: Data is missing. Moving to HUMAN INTERRUPTER ---")
# # #         return "human_interrupter_node"

# # #     # Secondary check: Safety
# # #     if not state.get("is_safe", True):
# # #         return "human_interrupter_node"

# # #     # Only if data is complete and safe do we check the Mode
# # #     mode = state.get("mode", "quick")
# # #     if mode == "planner":
# # #         return "planner_node"
    
# # #     return "quick_lookup_node"
# # # # --- 2. Build the Graph ---
# # # builder = StateGraph(AgentState)

# # # builder.add_node("rewrite_node", rewrite_node)
# # # builder.add_node("human_interrupter_node", human_interrupter_node)
# # # builder.add_node("planner_node", planner_node)
# # # builder.add_node("deep_research_node", deep_research_node)
# # # builder.add_node("quick_lookup_node", quick_lookup_node)
# # # builder.add_node("synthesizer_node", synthesizer_node)

# # # # --- 3. Define the Edges ---
# # # builder.add_edge(START, "rewrite_node")

# # # # Use ONLY ONE conditional edge from rewrite_node
# # # builder.add_conditional_edges(
# # #     "rewrite_node",
# # #     master_router,
# # #     {
# # #         "human_interrupter_node": "human_interrupter_node",
# # #         "planner_node": "planner_node",
# # #         "quick_lookup_node": "quick_lookup_node"
# # #     }
# # # )

# # # # Human feedback loops back to rewrite to re-process the new info
# # # builder.add_edge("human_interrupter_node", "rewrite_node")

# # # # Research paths
# # # builder.add_edge("planner_node", "deep_research_node")
# # # builder.add_edge("deep_research_node", "synthesizer_node")
# # # builder.add_edge("quick_lookup_node", "synthesizer_node")

# # # # CRITICAL: This ensures the process finishes
# # # builder.add_edge("synthesizer_node", END)

# # # # Compile
# # # app = builder.compile(checkpointer=memory)

# # # # --- 7. Execution Logic (For Testing) ---
# # # if __name__ == "__main__":
    
    
# # #     # Thread ID is required for stateful memory
# # #     config = {"configurable": {"thread_id": "travel_agent_v1"}}
    
# # #     # Example: User provides a vague query
# # #     initial_input = {"messages": [HumanMessage(content="Plan a trip to Kashmir for me and my toddler")]}
# # #     # Run the graph
# # #     # When it hits the 'interrupt' in your node, this loop will pause.
# # #     for event in app.stream(initial_input, config, stream_mode="values"):
# # #         last_message = event["messages"][-1]
# # #         print(f"\n[Node Update]: {last_message.content[:5000]}...")

# # #     # Logic to check if we are waiting for human input
# # #     state = app.get_state(config)
# # #     if state.next:
# # #         # If the graph is stopped at the interrupter
# # #         user_response = input("\nAGENT NEEDS INFO: ")
        
# # #         # RESUME the graph with the new input
# # #         # This triggers the 'Command(resume=...)' logic inside your node
# # #         for event in app.stream(None, config, stream_mode="values"):
# # #              last_message = event["messages"][-1]
# # #              print(f"\n[Resumed Update]: {last_message.content[:100]}...")
# # import os
# # from typing import Literal
# # from langgraph.graph import StateGraph, START, END
# # from langgraph.checkpoint.memory import MemorySaver
# # from langgraph.types import Command
# # from langchain_core.messages import HumanMessage

# # # 1. Import your modular state and nodes
# # from state import AgentState
# # from nodes.rewrite import rewrite_node
# # from nodes.planner import planner_node
# # from nodes.deep_research import deep_research_node
# # from nodes.quick_lookup import quick_lookup_node
# # from nodes.synthesizer import synthesizer_node
# # from nodes.human_interruptor import human_interrupter_node

# # # 2. Setup Persistence (Crucial for stateful interruptions)
# # memory = MemorySaver()

# # # 3. Define the Clean Router Logic
# # def master_router(state: AgentState) -> Literal["human_interrupter_node", "planner_node", "quick_lookup_node"]:
# #     # PRIORITY 1: Check if the query is marked incomplete by rewrite_node
# #     if state.get("is_incomplete", False):
# #         print("--- [ROUTER]: Information Missing -> Routing to Human ---")
# #         return "human_interrupter_node"

# #     # PRIORITY 2: Safety Check
# #     if not state.get("is_safe", True):
# #         print("--- [ROUTER]: Unsafe Query -> Routing to Human ---")
# #         return "human_interrupter_node"

# #     # PRIORITY 3: Execution Mode (Determined in rewrite_node)
# #     mode = state.get("mode", "quick")
# #     if mode == "planner":
# #         print("--- [ROUTER]: Complex Request -> Routing to Planner ---")
# #         return "planner_node"
    
# #     print("--- [ROUTER]: Simple Request -> Routing to Quick Lookup ---")
# #     return "quick_lookup_node"

# # # 4. Build the Graph
# # builder = StateGraph(AgentState)

# # # Add Nodes
# # builder.add_node("rewrite_node", rewrite_node)
# # builder.add_node("human_interrupter_node", human_interrupter_node)
# # builder.add_node("planner_node", planner_node)
# # builder.add_node("deep_research_node", deep_research_node)
# # builder.add_node("quick_lookup_node", quick_lookup_node)
# # builder.add_node("synthesizer_node", synthesizer_node)

# # # Define Logic Flow
# # builder.add_edge(START, "rewrite_node")

# # # Routing from Rewrite
# # builder.add_conditional_edges(
# #     "rewrite_node",
# #     master_router,
# #     {
# #         "human_interrupter_node": "human_interrupter_node",
# #         "planner_node": "planner_node",
# #         "quick_lookup_node": "quick_lookup_node"
# #     }
# # )

# # # Human loop back to rewrite to confirm info is now sufficient
# # builder.add_edge("human_interrupter_node", "rewrite_node")

# # # Research & Synthesis Paths
# # builder.add_edge("planner_node", "deep_research_node")
# # builder.add_edge("deep_research_node", "synthesizer_node")
# # builder.add_edge("quick_lookup_node", "synthesizer_node")
# # builder.add_edge("synthesizer_node", END)

# # # Compile
# # app = builder.compile(checkpointer=memory)

# # # 5. Robust Execution Logic
# # def run_interactive_agent(user_query: str):
# #     config = {"configurable": {"thread_id": "travel_session_001"}}
# #     initial_input = {"messages": [HumanMessage(content=user_query)]}

# #     print("\n--- Starting Travel Agent ---")
    
# #     # Execute until completion or interrupt
# #     # stream_mode="values" allows us to see the final output of each node
# #     for event in app.stream(initial_input, config, stream_mode="values"):
# #         if event.get("messages"):
# #             last_msg = event["messages"][-1].content
# #             print(f"\n[Node Update]: {last_msg[:200]}...")

# #     # HITL (Human-In-The-Loop) Loop
# #     while True:
# #         state = app.get_state(config)
        
# #         # If the graph is paused at the human_interrupter_node
# #         if state.next and "human_interrupter_node" in state.next:
# #             print("\n" + "="*30)
# #             user_response = input("AGENT NEEDS INFO (or type 'quit'): ")
            
# #             if user_response.lower() == 'quit':
# #                 break
                
# #             print(f"\n--- Resuming with: {user_response} ---")
            
# #             # Using Command(resume=...) to push the input into the 'interrupt' call
# #             for event in app.stream(Command(resume=user_response), config, stream_mode="values"):
# #                 if event.get("messages"):
# #                     last_msg = event["messages"][-1].content
# #                     print(f"\n[Update]: {last_msg[:200]}...")
# #         else:
# #             # Graph finished normally or reached END
# #             print("\n--- Workflow Completed ---")
# #             break

# # if __name__ == "__main__":
# #     run_interactive_agent("Plan a trip to Kashmir for me and my toddler")
# import os
# from langgraph.graph import StateGraph, START, END
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.types import Command
# from langchain_core.messages import HumanMessage
# import psycopg
# from psycopg_pool import ConnectionPool
# from langgraph.checkpoint.postgres import PostgresSaver
# # 1. Import your modular state and nodes
# from state import AgentState
# from nodes.rewrite import rewrite_node
# from nodes.planner import planner_node
# from nodes.deep_research import deep_research_node
# from nodes.quick_lookup import quick_lookup_node
# from nodes.synthesizer import synthesizer_node
# from nodes.human_interruptor import human_interrupter_node

# # 2. Setup Persistence (Necessary for the 'interrupt' function to work)
# #memory = MemorySaver()
# DB_URI = "postgresql://tarinijain@localhost:5432/travel_db" 

# # 2. Create a Connection Pool
# # The pool manages multiple database connections efficiently
# pool = ConnectionPool(conninfo=DB_URI, max_size=10)

# # 3. Initialize the Postgres Checkpointer
# checkpointer = PostgresSaver(pool)

# # 4. Initialize Tables (Run this once)
# # This creates the internal tables LangGraph needs to store thread state
# with pool.connection() as conn:
#     checkpointer.setup(conn)

# # 3. Initialize and Build the Graph
# builder = StateGraph(AgentState)

# # Add all nodes
# builder.add_node("rewrite_node", rewrite_node)
# builder.add_node("human_interrupter_node", human_interrupter_node)
# builder.add_node("planner_node", planner_node)
# builder.add_node("deep_research_node", deep_research_node)
# builder.add_node("quick_lookup_node", quick_lookup_node)
# builder.add_node("synthesizer_node", synthesizer_node)

# # 4. Define the Minimal Edge Logic
# # Since your nodes use Command(goto="..."), you only need starting and ending edges.
# builder.add_edge(START, "rewrite_node")

# # Fixed sequences (Research -> Synth)
# builder.add_edge("planner_node", "deep_research_node")
# builder.add_edge("deep_research_node", "synthesizer_node")
# builder.add_edge("quick_lookup_node", "synthesizer_node")
# builder.add_edge("synthesizer_node", END)

# # 5. Compile
# app = builder.compile(checkpointer=checkpointer)
# #app = builder.compile()

# # 6. Execution Logic for Testing (Handles Pauses/Resumes)
# # ... (imports and builder setup remain the same) ...

# # 6. Execution Logic for Testing
# def run_interactive_travel_agent():
#     config = {"configurable": {"thread_id": "travel_session_2026"}}
    
#     print("--- 🌍 Travel Agent v2.0 Initialized ---")
#     user_query = "Plan a weekend in Alibaug. We'll take the M2M ferry from Mumbai"
    
#     initial_input = {"messages": [HumanMessage(content=user_query)]}
    
#     # 1. INITIAL RUN
#     # This runs until the first END or the first interrupt()
#     for event in app.stream(initial_input, config, stream_mode="values"):
#         if event.get("messages"):
#             print(f"\n[Agent]: {event['messages'][-1].content[:5000]}...")

#     # 2. THE RESUME LOOP (The "Resume Condition")
#     # while True:
#     #     state = app.get_state(config)
        
#     #     # RESUME CONDITION: Is the graph currently paused at the human_interrupter_node?
#     #     if state.next and "human_interrupter_node" in state.next:
#     #         print("\n" + "="*40)
#     #         user_response = input("ACTION REQUIRED: ")
            
#     #         if user_response.lower() in ["quit", "exit"]:
#     #             print("Exiting...")
#     #             break
            
#     #         # Use Command(resume=...) to pass data back into the interrupt()
#     #         # Note: We pass None as the input because the state is already in the checkpointer
#     #         for event in app.stream(Command(resume=user_response), config, stream_mode="values"):
#     #             if event.get("messages"):
#     #                 print(f"\n[Agent]: {event['messages'][-1].content[:500]}...")
        
#     #     # TERMINATION CONDITION: If state.next is empty, the graph has reached END
#     #     else:
#     #         print("\n--- ✅ Trip Planning Complete ---")
#     #         break

# if __name__ == "__main__":
#     run_interactive_travel_agent()
# import os
# import psycopg
# from psycopg_pool import ConnectionPool
# from typing import Literal
# from langgraph.graph import StateGraph, START, END
# from langgraph.checkpoint.postgres import PostgresSaver # Updated import
# from langgraph.types import Command
# from langchain_core.messages import HumanMessage

# # 1. Import your modular state and nodes
# from state import AgentState
# from nodes.rewrite import rewrite_node
# from nodes.planner import planner_node
# from nodes.deep_research import deep_research_node
# from nodes.quick_lookup import quick_lookup_node
# from nodes.synthesizer import synthesizer_node
# from nodes.human_interruptor import human_interrupter_node

# # --- DATABASE SETUP ---
# # Update this string with your local Postgres credentials
# DB_URI = "postgresql://tarinijain@localhost:5432/travel_db"

# with psycopg.connect(DB_URI, autocommit=True) as conn:
#     checkpointer = PostgresSaver(conn)
#     checkpointer.setup()
#     print("✅ Database tables and concurrent indexes initialized.")

# # 2. Now create the Pool for the actual application runtime
# pool = ConnectionPool(conninfo=DB_URI, max_size=10)
# checkpointer = PostgresSaver(pool)

# # 3. Compile the app
# # ----------------------

# # 2. Initialize and Build the Graph
# builder = StateGraph(AgentState)

# # Add all nodes
# builder.add_node("rewrite_node", rewrite_node)
# builder.add_node("human_interrupter_node", human_interrupter_node)
# builder.add_node("planner_node", planner_node)
# builder.add_node("deep_research_node", deep_research_node)
# builder.add_node("quick_lookup_node", quick_lookup_node)
# builder.add_node("synthesizer_node", synthesizer_node)

# # 3. Define the Minimal Edge Logic
# # Nodes now use Command(goto="...") for internal routing
# builder.add_edge(START, "rewrite_node")

# # Fixed sequences (Research -> Synth)
# builder.add_edge("planner_node", "deep_research_node")
# builder.add_edge("deep_research_node", "synthesizer_node")
# builder.add_edge("quick_lookup_node", "synthesizer_node")
# builder.add_edge("synthesizer_node", END)

# # 4. Compile with the PERSISTENT checkpointer
# app = builder.compile(checkpointer=checkpointer)

# # 5. Execution Logic for Testing (CLI mode)
# def run_interactive_travel_agent():
#     # This thread_id is the "key" in your database
#     config = {"configurable": {"thread_id": "travel_session_2026"}}
    
#     print("--- 🌍 Travel Agent (Postgres Persistence) ---")
#     user_query = "Plan a weekend in Alibaug."
    
#     initial_input = {"messages": [HumanMessage(content=user_query)]}
    
#     # Run the graph (it will save state to Postgres automatically)
#     for event in app.stream(initial_input, config, stream_mode="values"):
#         if event.get("messages"):
#             print(f"\n[Agent]: {event['messages'][-1].content[:500]}...")

# if __name__ == "__main__":
#     run_interactive_travel_agent()
# 

import asyncio
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import HumanMessage
from langgraph.types import Command
import uuid
# Import your state and nodes
from state import AgentState
from nodes.rewrite import rewrite_node
from nodes.planner import planner_node
from nodes.deep_research import deep_research_node
from nodes.quick_lookup import quick_lookup_node
from nodes.synthesizer import synthesizer_node
from nodes.human_interruptor import human_interrupter_node

# Database configuration
DB_URI = "postgresql://tarinijain@localhost:5432/travel_db"
connection_kwargs = {"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row}

# --- 🛣️ Conditional Routing Logic ---
def route_after_rewrite(state: AgentState):
    """Decides where the graph goes after the query is rewritten/analyzed."""
    print(state)
    if not state.get("is_safe") or state.get("is_incomplete"):
        return "human_interrupter_node"
    
    # Check the 'mode' set by rewrite_node
    return "planner_node" if state.get("mode") == "planner" else "quick_lookup_node"

async def get_async_app():
    # 1. Setup Postgres Pool correctly
    # Set open=False to prevent the deprecated constructor-opening behavior
    pool = AsyncConnectionPool(
        conninfo=DB_URI, 
        max_size=20, 
        kwargs=connection_kwargs,
        open=False  # <--- Crucial fix for the warning
    )
    
    # 2. Explicitly open the pool and wait for it
    await pool.open() 
    
    # 3. Initialize Checkpointer
    checkpointer = AsyncPostgresSaver(pool)
    
    # Ensure the internal tables exist in your Postgres DB
    await checkpointer.setup()
    
    # 2. Initialize the Graph Builder
    builder = StateGraph(AgentState)

    # 3. Add all Modular Nodes
    builder.add_node("rewrite_node", rewrite_node)
    builder.add_node("human_interrupter_node", human_interrupter_node)
    builder.add_node("planner_node", planner_node)
    builder.add_node("deep_research_node", deep_research_node)
    builder.add_node("quick_lookup_node", quick_lookup_node)
    builder.add_node("synthesizer_node", synthesizer_node)

    # 4. Define the Connections (Edges)
    builder.add_edge(START, "rewrite_node")

    # Conditional branching from Rewrite
    builder.add_conditional_edges(
        "rewrite_node",
        route_after_rewrite,
        {
            "human_interrupter_node": "human_interrupter_node",
            "planner_node": "planner_node",
            "quick_lookup_node": "quick_lookup_node"
        }
    )

    # Recovery Loop: If human provides info, go back to rewrite for re-validation
    builder.add_edge("human_interrupter_node", "rewrite_node")

    # Planner Branch: Plan -> Deep Research -> Final Answer
    builder.add_edge("planner_node", "deep_research_node")
    builder.add_edge("deep_research_node", "synthesizer_node")

    # Quick Branch: Search -> Final Answer
    builder.add_edge("quick_lookup_node", "synthesizer_node")

    # Finish the workflow
    builder.add_edge("synthesizer_node", END)

    # 5. Compile the App
    return builder.compile(checkpointer=checkpointer)
async def run_interactive_test():
    """
    Test loop for the Travel Architect.
    It automatically detects if the agent is waiting for clarification.
    """
    app = await get_async_app()
    
    # Using a fixed thread_id so the DB remembers you if you restart
    config = {"configurable": {"thread_id": "test_session_2026"}}

    print("\n🌍 --- Travel Architect Terminal ---")
    print("Commands: 'exit' to quit, '/reset' for a new trip\n")

    while True:
        # 1. Fetch current graph state
        state = await app.aget_state(config)
        
        # 2. Dynamic Prompting: If graph is paused (next is not empty), get the AI's question
        if state.next:
            # We pull the question generated by your rewrite_node
            agent_question = state.values.get("rewritten_query", "Could you provide more details?")
            prompt = f"\n🤖 AGENT: {agent_question}\n🧑 Your Response: "
        else:
            prompt = "\n🧑 Plan your journey: "

        user_input = input(prompt).strip()

        # Handle Commands
        if not user_input: continue
        if user_input.lower() in ["exit", "quit"]: break
        if user_input.lower() == "/reset":
            config["configurable"]["thread_id"] = str(uuid.uuid4())
            print("✨ Conversation reset. Starting fresh!")
            continue

        # 3. Decision: Resume vs Start New
        if state.next:
            # Send the answer to the waiting 'interrupt()' in human_interrupter_node
            payload = Command(resume=user_input)
        else:
            # Start a fresh workflow turn
            payload = {"messages": [HumanMessage(content=user_input)]}

        # 4. Stream and Process Results
        print("⚙️  Processing...")
        async for mode, content in app.astream(payload, config, stream_mode=["updates", "messages"]):
            if mode == "updates":
                node_name = list(content.keys())[0]
                print(f"📍 Node: {node_name}")
                
            elif mode == "messages":
                chunk, metadata = content
                # Stream the synthesizer output token by token
                if metadata.get("langgraph_node") == "synthesizer_node":
                    print(chunk.content, end="", flush=True)
        
        print("\n" + "—"*40)

if __name__ == "__main__":
    try:
        asyncio.run(run_interactive_test())
    except KeyboardInterrupt:
        print("\n👋 Test cancelled.")

# if __name__ == "__main__":
#     async def test_run():
#         app = await get_async_app()
#         config = {"configurable": {"thread_id": "test_123"}}
#         inputs = {"messages": [HumanMessage(content="Plan a trip to Goa")]}
#         # async for event in app.astream(inputs, config, stream_mode="values"):
#         #     print(event)
    
#     asyncio.run(test_run())