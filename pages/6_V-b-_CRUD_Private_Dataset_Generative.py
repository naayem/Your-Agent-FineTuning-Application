import streamlit as st
import openai
import ast
import pymongo
from pymongo.errors import PyMongoError, DuplicateKeyError
import pandas as pd


# Session State also supports attribute based syntax
if 'generated_entry' not in st.session_state:
    st.session_state.generated_entry = []


def convert_to_list_of_dicts(data_str):
    # Convert single quotes for keys and outer boundaries of values to double quotes
    corrected_data_str = data_str\
        .replace("'role': 'system', 'content': '", '"role": "system", "content": "')\
        .replace("'}, {'role': 'user', 'content': '", '"}, {"role": "user", "content": "')\
        .replace("'}, {'role': 'assistant', 'content': '", '"}, {"role": "assistant", "content": "')\
        .replace("'}]", '"}]')
    st.write("CORRECTED")
    st.write(corrected_data_str)
    try:
        # Convert the string to a Python list of dictionaries
        data = ast.literal_eval(corrected_data_str)
        return data
    except Exception as e:
        # Handle any parsing errors
        st.error(f"Error: {e}")
        return []


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


nb_exchanges = st.number_input(
    "Number of Messages",
    value=1,
    min_value=1,
    max_value=1000,
    step=1
    )

system_message = "You are a helpful assistant"

exchanges = []
for i in range(nb_exchanges):
    user_message = f"user_message{i}"
    assistant_message = f"assistant_message{i}"
    exchanges.append({"user_message": user_message, "assistant_message": assistant_message})


with st.form("Generate Entry"):
    generated_edited_entry = []
    data = []
    prompt_gen_conv = st.text_area(
        "Prompt to generate a conversation\n",
        "Generate a conversation between a patient and its Doctor.\n"
        "The patient complain about dolor in its abdomen\n"
        "The doctor analyses the case and conclude just have an intoxication\n"
        f"Provide exactly {nb_exchanges} exchanges between the two protagonists\n",
        height=300)
    prompt_injection = '''
        The purpose of this generation is to create an artificial dataset to train an large language model.
        Make sure to not generate a string between double quotes (")
        Please provide your answer in the following format:
        ---------------------------------------------------
        '''
    conversation_format = [{"role": "system", "content": "**INSERT HERE A SYSTEM MESSAGE**"}]

    for i in range(nb_exchanges):
        conversation_format.append({"role": "user", "content": "**INSERT HERE AN USER MESSAGE**"})
        conversation_format.append({"role": "assistant", "content": "**INSERT HERE AN USER MESSAGE**"})

    selected_model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-3.5-turbo"])

    system_prompt_gen = '''
        You are an expert in synthetic dataset generation,
        answer entirely and only with the following list of dict format for openai chat messages:
        '''
    generation_input_prompt = [{"role": "system",
                                "content": system_prompt_gen},
                               {"role": "user",
                                "content": prompt_gen_conv + prompt_injection + conversation_format.__str__()}]
    if st.form_submit_button("Generate"):
        response = openai.ChatCompletion.create(
            model=selected_model,
            messages=generation_input_prompt
        )
        st.session_state.generated_entry = convert_to_list_of_dicts(response['choices'][0]['message']['content'])
        st.success("Generation completed!")

with st.form("Edit Generation and Add"):
    # Get the list of agent names and their corresponding IDs
    agent_names = [agent['name'] for agent in agents]
    agent_ids = {agent['name']: agent['_id'] for agent in agents}

    selected_agent_name = st.selectbox("Select Agent", agent_names)
    selected_agent_id = agent_ids[selected_agent_name]
    agent_prompt = next((agent["system_prompt"] for agent in agents if agent["name"] == selected_agent_name), None)

    st.text(f"System Prompt: {agent_prompt}")

    generated_edited_entry = st.data_editor(st.session_state.generated_entry, use_container_width=True)

    if st.form_submit_button("Add to Dataset"):
        try:
            conversation_collection.insert_one(
                {
                    "agent_id": selected_agent_id,
                    "messages": generated_edited_entry
                }
            )
            st.success("Conversation added successfully!")
        except PyMongoError as e:
            st.error(f"Database error: {e}")
        except pymongo.errors.DuplicateKeyError:
            st.error("A conversation with the same content already exists!")

# Display Conversations
conversations = list(conversation_collection.find({}))
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
st.dataframe(df, use_container_width=True)