from pymongo import MongoClient
from justai.application.schemas import agent_schema, conversation_schema

# Connect to MongoDB
client = MongoClient("")  # Replace with your MongoDB connection link
db = client['AgentConvoDB']   # Replace with your desired database name

# Create collections with validation
db.create_collection('agent', validator=agent_schema)
db.create_collection('conversation', validator=conversation_schema)

# Add Indexes
agent_collection = db['agent']
conversation_collection = db['conversation']

agent_collection.create_index("name", unique=True)
conversation_collection.create_index("agent_name")
