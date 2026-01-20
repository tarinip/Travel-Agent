# from langgraph.checkpoint.postgres import PostgresSaver
# from langgraph.checkpoint import Checkpoint
# from typing import Any, Dict, List

# class TravelAgentPostgresSaver(PostgresSaver):
#     """Custom PostgresSaver for travel agent session persistence"""
    
#     def __init__(self, connection_string: str):
#         super().__init__(connection_string)
        
#     def save_checkpoint(self, checkpoint: Checkpoint, metadata: Dict[str, Any]) -> None:
#         """Save checkpoint with custom metadata"""
#         # Add custom logic here if needed
#         super().save_checkpoint(checkpoint, metadata)
        
#     def get_checkpoint(self, thread_id: str) -> Checkpoint:
#         """Get checkpoint for a specific thread"""
#         return super().get_checkpoint(thread_id)
        
#     def list_checkpoints(self, thread_id: str) -> List[Checkpoint]:
#         """List all checkpoints for a thread"""
#         return super().list_checkpoints(thread_id)
import os
from sqlalchemy import create_engine
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from dotenv import load_dotenv

load_dotenv()

# 1. Get your connection string
db_url = os.getenv("CHAINLIT_DATABASE_URL")

if not db_url:
    print("❌ Error: CHAINLIT_DATABASE_URL not found in .env")
else:
    try:
        # Use a sync connection for this setup script
        sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        
        # 2. Initialize the layer
        print(f"🔄 Connecting to {sync_url}...")
        layer = SQLAlchemyDataLayer(sync_url)
        
        # 3. Use the engine from the layer to create tables
        # We use getattr to safely find the metadata
        metadata = getattr(layer, 'metadata', None) or getattr(layer, 'base', None).metadata
        
        metadata.create_all(layer.engine)
        print("✅ Success! The 'threads', 'steps', and 'users' tables have been created.")
        
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")