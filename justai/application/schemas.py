# Agent Schema
agent_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "system_prompt", "dataset_generation_prompts"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "The name of the agent"
            },
            "system_prompt": {
                "bsonType": "string",
                "description": "System's initial instruction or context-setting message"
            },
            "dataset_generation_prompts": {
                "bsonType": "object",
                "description": "A dictionary containing dataset generation prompts. Defaults to an empty dictionary.",
                "additionalProperties": {
                    "bsonType": "string"
                }
            }
        }
    }
}

# Conversation Schema
conversation_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["agent_name", "messages"],
        "properties": {
            "agent_name": {
                "bsonType": "string",
                "description": "The name of the agent"
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
            },
            "tags": {
                "bsonType": "array",
                "items": {
                    "bsonType": "string"
                },
                "description": "List of tags associated with the conversation"
            }
        }
    }
}

user_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["user_name"],
        "properties": {
            "user_name": {
                "bsonType": "string",
                "description": "The unique name or identifier of the user"
            }
        }
    }
}
