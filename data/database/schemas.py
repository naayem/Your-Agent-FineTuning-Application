# Agent Schema
agent_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "system_prompt"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "The name of the agent"
            },
            "system_prompt": {
                "bsonType": "string",
                "description": "System's initial instruction or context-setting message"
            }
        }
    }
}

# Conversation Schema
conversation_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["agent_id", "messages"],
        "properties": {
            "agent_id": {
                "bsonType": "objectId",
                "description": "Reference to the agent's ID in the Agent collection"
            },
            "messages": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["role", "content"],
                    "properties": {
                        "role": {
                            "bsonType": "string",
                            "enum": ["system", "user", "assistant"],
                            "description": "Role can be either system, user, or assistant"
                        },
                        "content": {
                            "bsonType": "string",
                            "description": "Content of the message"
                        }
                    }
                }
            }
        }
    }
}
