import streamlit as st

import justai
from justai.frameworks_and_drivers.dashboards.agent_dashboard import agent_management_dashboard
from justai.frameworks_and_drivers.dashboards.conversation_dashboard import conversation_management_dashboard
from justai.frameworks_and_drivers.dashboards.feedback_dashboard import FeedbackManagementDashboard
from justai.frameworks_and_drivers.dashboards.generate_synthetic_conversation import conversation_generator_dashboard
from justai.use_cases.feedback_use_cases import FeedbackUseCases
from justai.use_cases.user_use_cases import UserUseCases


if 'agent' not in st.session_state:
    st.session_state.agent = ""
if 'generated_conversation' not in st.session_state:
    st.session_state.generated_conversation = []

########################################################################################################################
# SIDEBAR
########################################################################################################################
repos = justai.frameworks_and_drivers.database_sidebar.database_sidebar()

if not repos:
    st.warning("Please configure the database connection first.")

agent_use_cases = justai.use_cases.agent_use_cases.AgentUseCases(
    repos["agent"],
    repos["backup"],
    repos["conversation"]
)
conversation_use_cases = justai.use_cases.conversation_use_cases.ConversationUseCases(
    repos["agent"],
    repos["conversation"],
    repos["backup"]
)

user_use_cases = UserUseCases(repos["user"])
feedback_use_cases = FeedbackUseCases(repos["feedback"])
feedback_management_dashboard = FeedbackManagementDashboard(feedback_use_cases, user_use_cases)

########################################################################################################################
# TABLES
########################################################################################################################

st.title("AI Conversation Generator")
st.write("""
Welcome to the LLM Dataset Generation Tool, a specialized application designed to streamline the creation of datasets
for training or fine-tuning large language models (LLMs).
In the world of machine learning, high-quality data is paramount.
This tool facilitates the generation of synthetic datasets that mimic real-world interactions
between a user and an assistant, based on customizable prompts.

The dataset generation prompt is at the heart of this process.
It serves as a set of instructions for the LLM,
guiding it to produce synthetic data that demonstrates how we envision the interaction between an assistant and a user.
By crafting detailed prompts, we can leverage the power of LLMs
to generate entire conversations with a specified number of exchanges.

Here's a brief example of the tool's capability:
Given a well-structured prompt,
the tool can create a synthetic conversation that mimics a real interaction.
Once generated, creators can fine-tune the conversation,
ensuring it adheres to the desired format for seamless integration into our database.

This approach not only saves significant time and effort in dataset creation
but also allows for the generation of diverse and rich scenarios
which are essential for the robust training of LLMs.
""")
st.caption("Please note that this tool is in an experimental phase,\
    and we highly value your feedback to understand its limitations and enhance its capabilities.")
st.markdown("""
<span style="color: #7D26CD;">
<strong>Ideas to make this tool better:</strong>
<ul>
    <li>Chain of prompts:
        <ol>
            <li>Create a conversation in full text.</li>
            <li>Extract each exchange into the correct format.</li>
            <li>XTRA: pre-step of asking the llm to explicit its reasoning.</li>
        </ol>
    </li>
    <li>Display the conversation in a chat format</li>
    <li>Add a video tutorial</li>
    <li>Use fine-tuned models for conversation generation tasks</li>
    <li>When a convo is saved into the conversation DB, save additionally the example of Conversation Generation</li>
</ul>
</span>
""", unsafe_allow_html=True)

agents = agent_use_cases.get_all()
conversations = conversation_use_cases.get_all()

# Select an Agent to work with
agent_names = [agent.name for agent in agents]
try:
    default_index = agent_names.index(st.session_state.agent)
except ValueError:
    default_index = 0
agent_name = st.selectbox(
    "With Which Agent do you want to work with?",
    agent_names,
    index=default_index)
st.session_state.agent = agent_name
if not agent_name:
    st.error("Please select an agent")

st.divider()
conversation_generator_dashboard(agent_use_cases, conversation_use_cases, agent_name)

st.divider()
st.header("other Dashboards")
with st.expander("Agent Management Dashboard"):
    agent_management_dashboard(agent_use_cases, agents, expander=True)

with st.expander("# Conversation Management Dashboard", expanded=False):
    conversation_management_dashboard(
        agent_use_cases,
        conversation_use_cases,
        [agent.name for agent in agents],
        conversations,
        expander=False
    )

st.divider()
with st.expander(":green[**Any Feedback?**]"):
    feedback_management_dashboard.create_new_feedback()
