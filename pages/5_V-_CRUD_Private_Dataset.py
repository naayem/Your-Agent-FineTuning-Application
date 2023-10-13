import streamlit as st
import openai
########################################################################################################################
# SIDEBAR
########################################################################################################################
with st.sidebar:
    st.title(' JAW OpenAI FineTuning 👁️')
    st.button("Reset", type="primary")

########################################################################################################################
# TABLES
########################################################################################################################
st.caption("🤖 For a better experience go to the settings and activate the wide mode")

col1, col2 = st.columns(2)

with col1.form("New entry"):
    nb_exchanges = st.number_input(
        "Number of Messages",
        value=1,
        min_value=1,
        max_value=1000,
        step=1
        )

    system_message = st.text_input(
        "System Message",
        value="You are a helpful assistant"
        )

    exchanges = []
    for i in range(nb_exchanges):
        user_message = st.text_input(
            f"User Message {i+1}",
            value="What's pythagoras theorem?",
            key=f"user_{i}"
            )
        assistant_message = st.text_input(
            f"Assistant Message {i+1}",
            value="Pythagoras theorem is a^2 + b^2 = c^2",
            key=f"assistant_{i}"
            )
        exchanges.append((user_message, assistant_message))
    test_data = st.data_editor(exchanges)
    st.write(test_data)

    st.form_submit_button("Add to dataset")

conversation = [
    {"role": "system", "content": system_message}
]

for user_message_exchange, assistant_message_exchange in exchanges:
    conversation.append({"role": "user", "content": user_message_exchange})
    conversation.append({"role": "system", "content": assistant_message_exchange})

st.table(conversation)
test_data = st.data_editor(conversation, use_container_width=True)
st.write(test_data)

with col2.form("Generate Entry"):
    prompt_gen_conv = st.text_area(
        "Prompt to generate a conversation\n",
        "Generate a conversation between a patient and its Doctor.\n"
        "The patient complain about dolor in its abdomen\n"
        "The doctor analyses the case and conclude just have an intoxication\n"
        f"Provide exactly {nb_exchanges} exchanges between the two protagonists\n",
        height=300)
    prompt_injection = '''
        The purpose of this generation is to create an artificial dataset to train an large language model.
        Please provide your answer in the following format:
        ---------------------------------------------------
        '''
    conversation_format = [{"role": "system", "content": "**INSERT HERE A SYSTEM MESSAGE**"}]

    for i in range(nb_exchanges):
        conversation_format.append({"role": "user", "content": "**INSERT HERE AN USER MESSAGE**"})
        conversation_format.append({"role": "assistant", "content": "**INSERT HERE AN USER MESSAGE**"})

    generated_conversation = st.text_area(
        label="Generate conversation",
        value=conversation_format.__str__(),
        height=600
        )
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
        st.write(generation_input_prompt)
        comment = '''
        response = openai.ChatCompletion.create(
            model=selected_model,
            messages=conversation_format
        )
        st.write(response['choices'][0]['message']['content'])
        '''
