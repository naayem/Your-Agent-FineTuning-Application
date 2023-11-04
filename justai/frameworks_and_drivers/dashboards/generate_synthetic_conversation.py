from time import sleep
from typing import List
import openai
import pandas as pd
import streamlit as st
import ast
from streamlit_extras.dataframe_explorer import dataframe_explorer


from justai.entities.agent import Agent
from justai.use_cases.agent_use_cases import AgentUseCases
from justai.use_cases.conversation_use_cases import ConversationUseCases


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
        .replace("'}]", '"}]')\
        .replace("'} ]", '"}]')

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


def create_agent_conversation_generation_prompt(agent_use_cases: AgentUseCases, agent_name: str):
    with st.form("Create a dataset generation prompt for an agent"):
        dgp_label = st.text_input(
            "Dataset Generation Prompt Label",
            help="Lawyer Cabinet Consultation, neighbors conflict "
        )
        dataset_generation_prompt = st.text_area("Dataset Generation Prompt for an Agent", height=300)
        submit_dgp = st.form_submit_button("Create the dataset generation prompt")

        if (submit_dgp and dgp_label and dataset_generation_prompt and agent_name):
            try:
                agent_use_cases.add_dataset_generation_prompt(
                    agent_name,
                    dgp_label,
                    dataset_generation_prompt
                )
                st.success(f"The Dataset Generation Prompt:\n\
                    of Agent {agent_name},\n\
                    named with label '{dgp_label}',\n\
                    have been created successfully!")
                sleep(3)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def edit_and_post_json_conversation(
    agent_name: str,
    agent_use_cases: AgentUseCases,
    conversation_use_cases: ConversationUseCases,
    generated_conversation
):
    selected_agent = agent_use_cases.get_one(agent_name)
    with st.form("Edit Generation and Add"):
        st.text(f"System Prompt: {selected_agent.system_prompt}")

        generated_edited_entry = st.data_editor(generated_conversation, use_container_width=True)

        if st.form_submit_button("Add to Dataset"):
            try:
                conversation_use_cases.create(agent_name, generated_edited_entry)
                st.rerun()
                st.success("Conversation added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")


def select_a_conversation_generation_prompt(agent: Agent):
    conversation_gen_prompts = ["None"]
    if agent:
        conversation_gen_prompts.extend(list(agent.dataset_generation_prompts.keys()))

    agent_cgp_key = st.selectbox("Select agent's conversation generation prompt", conversation_gen_prompts)
    return agent_cgp_key


def conversation_generator_pipeline(agent: Agent, agent_cgp_key: str) -> List:
    """_summary_
    Current Pipeline for Conversation Generation:
    1. Description of the conversation to generate
    2. Instruction for number of messages for conversation generation format
    3. Description prompt for conversation generation format
    4. Template for conversation generation format
    5. Use a model to generate a conversation with a prompt

    Returns:
        _type_: _description_
    """
    generated_conversation = []

    system_prompt_gen = '''
        You are an expert in synthetic dataset generation,
        answer entirely and only with the following list of dict format for openai chat messages:
        '''

    # Injecting description of the conversation to generate
    prompt_gen_conv = st.text_area(
        "Description of the conversation to generate",
        agent.dataset_generation_prompts[agent_cgp_key] if agent_cgp_key != "None" else "",
        height=300
    )

    # Injecting instruction for number of messages for conversation generation format
    nb_exchanges = st.number_input(
        "Number of Messages",
        value=1,
        min_value=1,
        max_value=1000,
        step=1
        )
    prompt_gen_conv_nb = st.text_area(
        "Prompt for conversation length",
        f"Provide exactly {nb_exchanges} exchanges between the two protagonists\n"
        )

    # Injecting description prompt for conversation generation format
    conversation_generation_format_description = '''
        The purpose of this generation is to create an artificial dataset to train an large language model.
        Make sure to not generate a string between double quotes (")
        Please provide your answer in the following format:
        ---------------------------------------------------
        '''

    # Injecting template for conversation generation format
    conversation_format_template = [{"role": "system", "content": "**INSERT HERE A SYSTEM MESSAGE**"}]
    for i in range(nb_exchanges):
        conversation_format_template.append({"role": "user", "content": "**INSERT HERE AN USER MESSAGE**"})
        conversation_format_template.append({"role": "assistant", "content": "**INSERT HERE AN USER MESSAGE**"})
        # Combine all prompts into a single prompt for conversation generation
        generation_input_prompt = [
            {
                "role": "system",
                "content": system_prompt_gen},
            {
                "role": "user",
                "content": prompt_gen_conv + prompt_gen_conv_nb +
                        conversation_generation_format_description + conversation_format_template.__str__()
            }
        ]

    # Use a model to generate a conversation with a prompt
    with st.form("Generate Entry"):
        selected_model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-3.5-turbo", "gpt-4"])

        if st.form_submit_button("Generate"):
            response = openai.ChatCompletion.create(
                model=selected_model,
                messages=generation_input_prompt
            )
            generated_conversation = convert_to_list_of_dicts(response['choices'][0]['message']['content'])
            st.session_state.generated_conversation
            st.success("Generation completed!")
            sleep(2)
            return generated_conversation

    return generated_conversation


def display_data_generation_prompts(agent: Agent):
    data_list = [
        {
            'label': k,
            'conversation generation prompt': v
        } for k, v in agent.dataset_generation_prompts.items()
    ]
    flattened_df = pd.DataFrame(data_list)
    filtered_conv_df = dataframe_explorer(flattened_df, case=False)
    st.dataframe(filtered_conv_df, use_container_width=True)


def conversation_generator_dashboard(
    agent_use_cases: AgentUseCases,
    conversation_use_cases: ConversationUseCases,
    agent_name: str,
):
    agent = agent_use_cases.get_one(agent_name)

    st.header("Conversation Generation")
    st.subheader("Select a Conversation Generation Prompt already save for this Agent, None chosen by default")

    # Display an Agent's Conversation Generation Prompts
    with st.expander("Have a look at the Agent's Conversation Generation Prompts", expanded=False):
        display_data_generation_prompts(agent)
    agent_cgp_key = select_a_conversation_generation_prompt(agent)

    st.subheader("Generate a conversation with descriptions and instructions")
    generated_conversation = conversation_generator_pipeline(agent, agent_cgp_key)

    st.subheader("Edit and save the generated conversation")
    edit_and_post_json_conversation(agent_name, agent_use_cases, conversation_use_cases, generated_conversation)

    st.subheader("Save a new conversation generation prompt to reuse later")
    st.write("Avoid rewriting the same prompts to generate over and over again.\
                Write a pre-prompt here to save a scenario or instructions to guide the conversation generation.\
                Expand this box to save a new conversation generation prompt")
    with st.expander("Save a new conversation generation prompt", expanded=False):
        create_agent_conversation_generation_prompt(agent_use_cases, agent_name)
