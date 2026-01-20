import os
import chainlit.data as cl_data
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from dotenv import load_dotenv

load_dotenv()

connection_url = os.getenv("CHAINLIT_DATABASE_URL")

if connection_url:
    try:
        # Pass the URL as a positional argument (no keyword)
        cl_data._data_layer = SQLAlchemyDataLayer(connection_url)
        print("✅ Chainlit Data Layer initialized successfully.")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")