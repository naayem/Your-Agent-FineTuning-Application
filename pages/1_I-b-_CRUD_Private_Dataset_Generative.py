import streamlit as st
import openai
import ast
import justai

# Session State also supports attribute based syntax
if 'generated_entry' not in st.session_state:
    st.session_state.generated_entry = []


def convert_to_list_of_dicts(data_str):
    # Convert single quotes for keys and outer boundaries of values to double quotes
    corrected_data_str = data_str\
        .replace("'role'", '"role"')\
        .replace("'user'", '"user"')\
        .replace("'assistant'", '"assistant"')\
        .replace("'content'", '"content"')\
        .replace("'system'", '"system"')\
        .replace("'assistant", '"assistant')\
        .replace("'},", '"},')\
        .replace(": '", ': "')\
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
repos = justai.frameworks_and_drivers.database_sidebar.database_sidebar()

if not repos:
    st.warning("Please configure the database connection first.")

agent_use_cases = justai.use_cases.agent_use_cases.AgentUseCases(repos["agent"], repos["backup"], repos["conversation"])
conversation_use_cases = justai.use_cases.conversation_use_cases.ConversationUseCases(repos["agent"], repos["conversation"], repos["backup"])

########################################################################################################################
# TABLES
########################################################################################################################
st.caption("🤖 For a better experience go to the settings and activate the wide mode")


# Display Agents
st.subheader("Agents")
agents = agent_use_cases.get_all()
agent_names = [agent.name for agent in agents]
# Convert list of Agent objects to list of dictionaries
agents_data = [agent.to_dict() for agent in agents]
st.dataframe(agents_data)

# Add a new agent
with st.form("Agent form"):
    agent_create_name = st.text_input("Agent Name")
    system_prompt = st.text_input("System Prompt for Agent")
    submit_agent = st.form_submit_button("Add Agent")

    if submit_agent and agent_create_name and system_prompt:
        try:
            agent_use_cases.create(agent_create_name, system_prompt)
            st.rerun()
            st.success(f"Agent {agent_create_name} added successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

# Add a create agent specific prompt
sel_agent_dgp_add_name = st.selectbox("Select Agent for dgp", agent_names)
if not sel_agent_dgp_add_name:
    st.error("Please select an agent")

with st.form("Agent dataset generation prompt create form"):
    specific_prompt_label = st.text_input("Specific prompt label")
    specific_agent_prompt = st.text_area("specific prompt for an Agent", height=300)
    submit_specific_prompt = st.form_submit_button("Add specific prompt")

    if (submit_specific_prompt and specific_prompt_label and specific_agent_prompt and sel_agent_dgp_add_name):
        try:
            agent_use_cases.add_dataset_generation_prompt(
                sel_agent_dgp_add_name,
                specific_prompt_label,
                specific_agent_prompt
            )
            st.rerun()
            st.success(f"Agent {sel_agent_dgp_add_name}' DGP {specific_prompt_label} added successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

# Select and agent and display its dataset generation prompts
st.subheader("Dataset generation prompts for selection")
agent_dgp_display_name = st.selectbox("Select Agent to display its dataset generation prompt", agent_names)
agent_dgp_display = None


def display_data_generation_prompts(agent_dgp_display_name: str):
    agent_dgp_display = agent_use_cases.get_one(agent_dgp_display_name)
    st.dataframe(agent_dgp_display.dataset_generation_prompts)
    return agent_dgp_display


agent_dgp_display = display_data_generation_prompts(agent_dgp_display_name)
dgps = ["None"]
if agent_dgp_display:
    dgps.extend(list(agent_dgp_display.dataset_generation_prompts.keys()))
st.write("dgps", dgps)
agent_dgp_key = st.selectbox("Select agent's data generation prompt", dgps)

generated_edited_entry = []
prompt_gen_conv = st.text_area(
    "Prompt for generation",
    agent_dgp_display.dataset_generation_prompts[agent_dgp_key],
    height=300
)


nb_exchanges = st.number_input(
    "Number of Messages",
    value=1,
    min_value=1,
    max_value=1000,
    step=1
    )
prompt_gen_conv_nb = st.text_area(
    "Prompt for conversaton length",
    f"Provide exactly {nb_exchanges} exchanges between the two protagonists\n"
    )

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

system_prompt_gen = '''
    You are an expert in synthetic dataset generation,
    answer entirely and only with the following list of dict format for openai chat messages:
    '''
generation_input_prompt = [
    {"role": "system",
     "content": system_prompt_gen},
    {"role": "user",
     "content": prompt_gen_conv + prompt_gen_conv_nb + prompt_injection + conversation_format.__str__()}
    ]


with st.form("Generate Entry"):
    selected_model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-3.5-turbo", "gpt-4"])

    if st.form_submit_button("Generate"):
        response = openai.ChatCompletion.create(
            model=selected_model,
            messages=generation_input_prompt
        )
        st.session_state.generated_entry = convert_to_list_of_dicts(response['choices'][0]['message']['content'])
        st.success("Generation completed!")

# Get the list of agent names and their corresponding IDs
selected_agent_name = st.selectbox("Select Agent", agent_names)
selected_agent = agent_use_cases.get_one(selected_agent_name)
with st.form("Edit Generation and Add"):
    st.text(f"System Prompt: {selected_agent.system_prompt}")

    generated_edited_entry = st.data_editor(st.session_state.generated_entry, use_container_width=True)

    if st.form_submit_button("Add to Dataset"):
        try:
            conversation_use_cases.create(selected_agent_name, generated_edited_entry)
            st.rerun()
            st.success("Conversation added successfully!")
        except Exception as e:
            st.error(f"Error: {e}")


# Display the conversations
st.header("Conversations")
all_conversations = conversation_use_cases.get_all()
all_conversations_for_df = [conversation.to_dict_stringify_messages() for conversation in all_conversations]
st.dataframe(all_conversations_for_df)
