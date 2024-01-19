import streamlit as st
import justai
from justai.frameworks_and_drivers.dashboards.feedback_dashboard import FeedbackManagementDashboard
from justai.use_cases.agent_use_cases import AgentUseCases
from justai.use_cases.conversation_use_cases import ConversationUseCases
from justai.use_cases.feedback_use_cases import FeedbackUseCases
from justai.use_cases.user_use_cases import UserUseCases

import locale

locale.getpreferredencoding = lambda: "UTF-8"

# App title
st.set_page_config(page_title="JAW OpenAI FineTuning 👁️", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = "None"
if "agent" not in st.session_state:
    st.session_state.agent = "None"
########################################################################################################################
# SIDEBAR
########################################################################################################################
repos = justai.frameworks_and_drivers.database_sidebar.database_sidebar()

if not repos:
    st.warning("Please configure the database connection first.")

agent_use_cases = AgentUseCases(repos["agent"], repos["backup"], repos["conversation"])
conversation_use_cases = ConversationUseCases(repos["agent"], repos["conversation"], repos["backup"])
user_use_cases = UserUseCases(repos["user"])
feedback_use_cases = FeedbackUseCases(repos["feedback"])
feedback_management_dashboard = FeedbackManagementDashboard(feedback_use_cases, user_use_cases)
########################################################################################################################
# Home Page
########################################################################################################################

<<<<<<< HEAD
st.title('JAW OpenAI Spinning Off Agents 👁️')
st.header('This is my home page I have to be creative here')
st.write("Let's show a dashboard of the current openAI jobs and let's maybe have a readme home page")
=======
st.title('Just Your Agent 👁️')

# Should be move to a separate file for better readability
st.markdown("""
### Your Journey to Creating a Personalized AI Agent

The mission of Just Your Agent is to empower you to create a personalized AI expert,
an assistant that enhances your interactions,
or a translator that bridges the gap between descriptions and application-specific commands.

Imagine having a conversation with an AI that not only understands your needs but also speaks in a tone and
with the knowledge that you've crafted.
This is not just any AI –
it's an AI agent tailored by you, for your specific use cases, and accessible via a simple API.

**The Process:**
To bring this personalized agent to life, we'll embark on a journey from raw conversation data
to a finely-tuned Large Language Model (LLM). Here's how it unfolds:

1. **Craft Conversations:** Like a playwright,
you'll write the script for your AI by creating conversations that teach it how to interact.
2. **Build a Dataset:** These conversations become a dataset,
the foundation upon which your AI agent learns.
3. **Fine-Tune the AI:** With this dataset,
we'll fine-tune the AI to imbue it with the nuances of your specific requirements.
4. **Deploy Your Agent:** Once trained,
your agent is ready to perform its role, accessible to you anytime through an API.

Ready to mold AI into your personal expert? Let's get started with the basics!

---
""", unsafe_allow_html=True)
>>>>>>> c6a8f0f (Remove unused files and update dependencies)

# Fetch list of all users for authentication
users = user_use_cases.get_all()
user_names = [user.user_name for user in users]

<<<<<<< HEAD
try:
    default_index = user_names.index(st.session_state.user)
except ValueError:
    default_index = 0  # or another default value like None
# User authentication
st.session_state.user = st.selectbox(
    "Please select your username:",
    user_names,
    index=default_index,
    format_func=str
=======

# function to update components and session state simutaneously on change
def _set_user_memory():
    st.session_state.user = st.session_state.main_user_select


# function to update components and session state simutaneously on change
def _set_agent_memory():
    st.session_state.agent = st.session_state.main_agent_select


# Manage the case where there are no users
try:
    default_user_index = user_names.index(st.session_state.user)
except ValueError:
    default_user_index = 0  # or another default value like None

# User authentication
st.selectbox(
    "Please select your username:",
    user_names,
    index=default_user_index,
    key="main_user_select",
    on_change=_set_user_memory,
>>>>>>> c6a8f0f (Remove unused files and update dependencies)
)

# Display welcome message after authentication
if st.session_state.user:
    st.write(f"Welcome, {st.session_state.user}!")

# Fetch list of all users for authentication
agents = agent_use_cases.get_all()
agent_names = [agent.name for agent in agents]

<<<<<<< HEAD
try:
    default_index = agent_names.index(st.session_state.agent)
except ValueError:
    default_index = 0  # or another default value like None
=======
# Manage the case where there are no agents
try:
    default_agent_index = agent_names.index(st.session_state.agent)
except ValueError:
    default_agent_index = 0  # or another default value like None

>>>>>>> c6a8f0f (Remove unused files and update dependencies)
# Agent Selection
st.session_state.agent = st.selectbox(
    "Select an agent to work with:",
    agent_names,
<<<<<<< HEAD
    index=default_index,
    format_func=str
=======
    index=default_agent_index,
    key="main_agent_select",
    on_change=_set_agent_memory
>>>>>>> c6a8f0f (Remove unused files and update dependencies)
)

# Display ready message after agent selection
if st.session_state.user:
    st.write(f"{st.session_state.agent} is at your service!")

with st.sidebar:
    st.divider()
    with st.expander(":green[**Any Feedback?**]"):
        feedback_management_dashboard.create_new_feedback()
<<<<<<< HEAD
=======

# Should be move to a separate file for better readability
st.expander("👋 New here? Click for guidance!", expanded=True).markdown("""
### Welcome to JustYourAgent!

If you're stepping into the world of AI-driven conversations, here's a quick guide to get you started:

#### 1. Manage Users:
Create your personal profile on the "Manage Users" page. Choose a username to identify yourself on our platform.
This username will be your identity for all interactions.

**What you can do here:**
- **Create Your Profile:** Choose a username to get started.
- **Edit Profile:** You can change your username anytime.
- **Remove Profile:** If necessary, you can delete your profile.

#### 2. Manage Agents:
Visit "Manage Agents" to set up your agent. Imagine you're assigning a role to an actor;
the agent is your character, and the system prompt is the script guiding its behavior.

**Understanding System Prompts:**
A system prompt guides the model on how to act. For example, instruct the model to behave like a Product Manager,
detailing the specific tasks and responsibilities of that role.

#### 3. Manage Conversations:
Use the "Manage Conversations" page to create and refine the dialogues for your agent.
This is your scriptwriting room where you teach the AI through example conversations.

#### 4. Chatbot Page:
The "Chatbot" page offers a dynamic way to interact with the AI.
You can have real-time conversations, save them, and modify past responses to improve communication flow.

#### 5. Creating a Dataset:
After you have a collection of conversations, you'll compile them into a dataset.
This dataset is crucial for training your agent to understand and engage in various scenarios.

**Process:**
- **Gather Conversations:** We bring together conversations from all users.
- **Quality Check:** We review the conversations to correct any mistakes and refine the content.
- **Cost Assessment:** We provide an overview of the costs associated with training the agent.

#### 6. Manage Fine-Tuning:
On the "Manage Fine-Tuning" page, you'll fine-tune your agent's interactions,
similar to giving an actor direction to better portray a character.
This step doesn't impart new knowledge but rather hones the agent's tone and style.

**Ready to start?** Collapse this guide and choose "Manage Users" from the menu to begin your AI adventure!
""", unsafe_allow_html=True)
>>>>>>> c6a8f0f (Remove unused files and update dependencies)
