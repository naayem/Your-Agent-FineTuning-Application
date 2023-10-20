import streamlit as st
import pymongo
from pymongo.errors import PyMongoError, DuplicateKeyError
import pandas as pd



st.set_page_config(layout="wide")

########################################################################################################################
# SIDEBAR
########################################################################################################################
with st.sidebar:
    st.title(' JAW OpenAI FineTuning 👁️')

    if 'MONGODB_SRV' in st.secrets:
        mongodb_link = st.secrets['MONGODB_SRV']
        my_client = pymongo.MongoClient(mongodb_link)
        st.success('MongoDB link provided!', icon='✅')
    else:
        mongodb_link = st.text_input(
            "Enter an OpenAI API token ",
            value="").strip('"')
        if not mongodb_link.startswith('mongodb+srv'):
            mongodb_link = None
            st.warning('Please enter your mongoDB link!', icon='⚠️')
        else:
            st.success('Proceed to develop your dataset!', icon='👉')

    st.button("Reset", type="primary")

########################################################################################################################
# TABLES
########################################################################################################################
st.caption("🤖 For a better experience go to the settings and activate the wide mode")

db_list = my_client.list_database_names()
db_sel = st.selectbox("Select db", db_list)
db = my_client[db_sel]
agent_collection = db['agent']
conversation_collection = db['conversation']

# Display Agents
agents = list(agent_collection.find({}))
st.subheader("Agents")
st.dataframe(agents)

# Add a new agent
with st.form("Agent form"):
    agent_name = st.text_input("Agent Name")
    system_prompt = st.text_input("System Prompt for Agent")
    submit_agent = st.form_submit_button("Add Agent")

    if submit_agent and agent_name and system_prompt:
        try:
            agent_collection.insert_one({"name": agent_name, "system_prompt": system_prompt})
            st.success(f"Agent {agent_name} added successfully!")
        except DuplicateKeyError:
            st.error(f"Agent {agent_name} already exists!")
        except PyMongoError as e:
            st.error(f"Database error: {e}")

# Delete an agent
with st.form("Delete Agent form"):
    agent_names = [agent['name'] for agent in agents]
    selected_agent_name = st.selectbox("Select Agent to Delete", agent_names)
    delete_agent = st.form_submit_button("Delete Agent")

    if delete_agent and selected_agent_name:
        try:
            # Fetch the agent's ID for the selected agent name
            selected_agent_id = next((agent["_id"] for agent in agents if agent["name"] == selected_agent_name), None)

            if not selected_agent_id:
                st.error(f"Agent {selected_agent_name} not found!")


            # Fetch linked conversations for the selected agent
            linked_conversations = list(conversation_collection.find({"agent_id": selected_agent_id}))

            if linked_conversations:
                # Insert the linked conversations into the backup collection
                backup_collection = db["backup"]
                backup_collection.insert_many(linked_conversations)

                # Delete the linked conversations from the conversation_collection
                conversation_collection.delete_many({"agent_id": selected_agent_id})
            
            # Delete the agent
            agent_collection.delete_one({"_id": selected_agent_id})

            st.success(f"Agent {selected_agent_name} deleted successfully!")
        except PyMongoError as e:
            st.error(f"Database error: {e}")


# Modify an agent
with st.form("Modify Agent form"):
    agent_names = [agent['name'] for agent in agents]
    selected_agent_name = st.selectbox("Select Agent to Modify", agent_names)
    new_agent_name = st.text_input("New Agent Name", value=selected_agent_name)
    current_system_prompt = next((agent["system_prompt"] for agent in agents if agent["name"] == selected_agent_name), "")
    new_system_prompt = st.text_input("New System Prompt for Agent", value=current_system_prompt)
    modify_agent = st.form_submit_button("Modify Agent")

    if modify_agent and new_agent_name and new_system_prompt:
        try:
            # Fetch the agent's ID for the selected agent name
            selected_agent_id = next((agent["_id"] for agent in agents if agent["name"] == selected_agent_name), None)

            if not selected_agent_id:
                st.error(f"Agent {selected_agent_name} not found!")


            # Update the agent in the agent collection
            agent_collection.update_one(
                {"_id": selected_agent_id},
                {"$set": {"name": new_agent_name, "system_prompt": new_system_prompt}}
            )

            # Update the system prompt in the associated entries of the conversation collection
            conversation_collection.update_many(
                {"agent_id": selected_agent_id},
                {"$set": {"messages.$[elem].content": new_system_prompt}},
                array_filters=[{"elem.role": "system"}]
            )

            st.success(f"Agent {selected_agent_name} modified successfully!")
        except PyMongoError as e:
            st.error(f"Database error: {e}")



# Display Conversations
conversations = list(conversation_collection.find({}))
st.subheader("Conversations")
# Create an empty list to store the transformed conversations
transformed_conversations = []

for conversation in conversations:
    # Get the agent_name using agent_id
    agent = agent_collection.find_one({"_id": conversation["agent_id"]})
    agent_name = agent["name"] if agent else None
    
    # Append to the list
    transformed_conversations.append({
        "ID": conversation["_id"],
        "agent_id": conversation["agent_id"],
        "agent_name": agent_name,
        "messages": repr(conversation["messages"])
    })

# Convert the list to a DataFrame
df = pd.DataFrame(transformed_conversations)

# Display the DataFrame in Streamlit
st.subheader("Conversations")
st.dataframe(df)

nb_exchanges = st.number_input("Number of Messages", value=1, min_value=1, max_value=1000, step=1)
# Add a new conversation
with st.form("Conversation form"):
    # Get the list of agent names and their corresponding IDs
    agent_names = [agent['name'] for agent in agents]
    agent_ids = {agent['name']: agent['_id'] for agent in agents}

    selected_agent_name = st.selectbox("Select Agent", agent_names)
    selected_agent_id = agent_ids[selected_agent_name]
    agent_prompt = next((agent["system_prompt"] for agent in agents if agent["name"] == selected_agent_name), None)

    st.text(f"System Prompt: {agent_prompt}")

    messages = [{"role": "system", "content": agent_prompt}]

    for i in range(nb_exchanges):
        user_message = f"user_message{i}"
        assistant_message = f"assistant_message{i}"
        messages.append(
            {
                "role": "user",
                "content": user_message
                }
            )
        messages.append(
            {
                "role": "assistant",
                "content": assistant_message
                }
            )

    messages = st.data_editor(messages, use_container_width=True)

    submit_conversation = st.form_submit_button("Add Conversation")

    if submit_conversation and messages:
        try:
            conversation_collection.insert_one(
                {
                    "agent_id": selected_agent_id,
                    "messages": messages
                }
            )
            st.success("Conversation added successfully!")
        except PyMongoError as e:
            st.error(f"Database error: {e}")
        except pymongo.errors.DuplicateKeyError:
            st.error("A conversation with the same content already exists!")
