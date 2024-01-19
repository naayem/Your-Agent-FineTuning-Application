from pymongo import MongoClient
from justai.application.schemas import agent_schema, conversation_schema, user_schema

# Connect to MongoDB
client = MongoClient("mongodb+srv://vincentnaayem:rKYU8c6KamkURYl1@youragent.tup5c.mongodb.net/?retryWrites=true&w=majority")  # Replace with your MongoDB connection link
db = client['AgentConvoDB']   # Replace with your desired database name

# Create collections with validation
db.create_collection('agent', validator=agent_schema)
db.create_collection('conversation', validator=conversation_schema)
db.create_collection('user', validator=user_schema)  # Adding user collection

# Add Indexes
agent_collection = db['agent']
conversation_collection = db['conversation']
user_collection = db['user']  # User collection


agent_collection.create_index("name", unique=True)
conversation_collection.create_index("agent_name")
user_collection.create_index("user_name", unique=True)  # Unique index for user_name
