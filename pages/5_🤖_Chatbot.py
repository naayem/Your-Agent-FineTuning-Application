import copy
import time
from types import NoneType
import openai
import streamlit as st
import justai
from justai.entities.conversation import Conversation, Message
from justai.frameworks_and_drivers.dashboards.feedback_dashboard import FeedbackManagementDashboard
from justai.use_cases.agent_use_cases import AgentUseCases
from justai.use_cases.conversation_use_cases import ConversationUseCases
from justai.use_cases.feedback_use_cases import FeedbackUseCases

from justai.use_cases.user_use_cases import UserUseCases
# ... other necessary imports


class StreamlitChatbot:
    DEFAULT_MESSAGE_SYSTEM = Message("system", "")
    DEFAULT_MESSAGE_ASSISTANT = Message("assistant", "How may I assist you today?")
    DEFAULT_CONVERSATION = Conversation("", [DEFAULT_MESSAGE_SYSTEM, DEFAULT_MESSAGE_ASSISTANT])
    NEW_CONVERSATION_LABEL = "New conversation"

    def __init__(
        self,
        user_use_cases: UserUseCases,
        agent_use_cases: AgentUseCases,
        conversation_use_cases: ConversationUseCases,
        openai_client: openai.OpenAI
    ):
        self.user_use_cases = user_use_cases
        self.agent_use_cases = agent_use_cases
        self.conversation_use_cases = conversation_use_cases
        self.selected_model = None
        self.previous_conversation = Conversation("", [], id="previous_conversation")
        self.current_conversation = None
        self.messages = [self.__class__.DEFAULT_MESSAGE_SYSTEM, self.__class__.DEFAULT_MESSAGE_ASSISTANT]
        self.conversation_tree = [self.__class__.DEFAULT_CONVERSATION]
        self.current_branch = 0
        self.flag_save = False
        self.conv_radio_index = 0
        self.openai_client = openai_client
        self._initialize_session_state()

    @property
    def user_name(self):
        return st.session_state.get('user', None)

    @user_name.setter
    def user_name(self, value):
        st.session_state.user = value
        self.conv_radio_index = 0

    @property
    def agent_name(self):
        return st.session_state.get('agent', None)

    @agent_name.setter
    def agent_name(self, value):
        st.session_state.agent = value
        self.conv_radio_index = 0

    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if "user" not in st.session_state:
            st.session_state.user = self.user_name
        if "agent_name" not in st.session_state:
            st.session_state.agent = self.agent_name

    @st.cache_data
    def fetch_openai_ft_models(_self):
        """Fetch OpenAI fine-tuned models."""
        classic_models = ["gpt-3.5-turbo", "gpt-4"]
        models_list = _self.openai_client.models.list().data

        # Filter models owned by 'epfl-42' and get their ids
        ft_openai_models = [model.id for model in models_list if model.owned_by == "epfl-42"]
        return classic_models + ft_openai_models

    def fetch_conversation_labels(self):
        """Fetch labels for conversations."""
        labels = {}
        agent = self.agent_use_cases.get_one(self.agent_name)

        labels[self.__class__.NEW_CONVERSATION_LABEL] = Conversation(
            agent_name=self.agent_name,
            messages=[
                Message("system", f"{agent.system_prompt}"),
                self.__class__.DEFAULT_MESSAGE_ASSISTANT
            ],
            tags=[self.user_name]
        )
        agent_convos = self.conversation_use_cases.get_by_agent_name(self.agent_name)
        user_convos = self.conversation_use_cases.search_in_conversations_by_tag(agent_convos, self.user_name)
        labels.update(self.conversation_use_cases.extract_labels_from_conversations(user_convos))
        return labels

    def handle_save_conversation_form(self):
        with st.form("save_conversation"):
            save_name = st.text_input("Save conversation as")
            submit_save_conv = st.form_submit_button("Submit save conversation")
            if submit_save_conv:
                new_conv_to_save = self.conversation_tree[self.current_branch]
                self.flag_save = False
                if self.current_conversation.id is None:
                    st.write("New conversation")
                    try:
                        st.write(new_conv_to_save)
                        self.conversation_use_cases.create(
                            new_conv_to_save.agent_name,
                            [message.to_dict() for message in new_conv_to_save.messages],
                            tags=[self.user_name, "label: " + save_name]
                        )
                        st.success(f"Conversation {save_name} saved successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        time.sleep(5)
                else:
                    st.write("Existing conversation")
                    try:
                        self.conversation_use_cases.overwrite(
                            self.conversation_tree[self.current_branch],
                            "label: " + save_name
                        )
                        st.session_state.n = save_name
                        st.success(f"Conversation {save_name} saved successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        time.sleep(5)

    def display_sidebar(self):
        """Display the sidebar for chatbot settings."""
        with st.sidebar:
            st.title(' JAW OpenAI Agents 👁️')
            self.selected_model = st.selectbox(
                "Select a fine-tuned model",
                self.fetch_openai_ft_models()
            )

            with st.expander('👨‍💻 User Setup', expanded=True):
                user_names = [user.user_name for user in self.user_use_cases.get_all()]
                agent_names = [agent.name for agent in self.agent_use_cases.get_all()]

                try:
                    default_user_index = user_names.index(self.user_name)
                except ValueError:
                    default_user_index = 0  # or another default value like None
                self.user_name = st.selectbox(
                    "Select a user",
                    user_names,
                    index=default_user_index
                )
                try:
                    default_agent_index = agent_names.index(self.agent_name)
                except ValueError:
                    default_agent_index = 0  # or another default value like None
                self.agent_name = st.selectbox(
                    "Select an Agent",
                    agent_names,
                    default_agent_index
                )

            if st.button("Save current conversation"):
                self.flag_save = True

            if self.flag_save:
                self.handle_save_conversation_form()

            labels = self.fetch_conversation_labels()

            def _set_conv_radio_index():
                keys_list = list(labels.keys())
                self.conv_radio_index = keys_list.index(st.session_state.n)\
                    if st.session_state.n in keys_list\
                    else keys_list.index(self.__class__.NEW_CONVERSATION_LABEL)

            conversation_radio_id = st.radio(
                "Select a conversation",
                labels,
                self.conv_radio_index,
                key='n',
                on_change=_set_conv_radio_index
            )
            self.current_conversation = labels[conversation_radio_id]
            if self.previous_conversation.id != self.current_conversation.id\
                    or self.agent_name != self.previous_conversation.agent_name\
                    or not conversation_use_cases.search_in_conversations_by_tag(
                        [self.previous_conversation],
                        self.user_name):
                # The conversation has changed, so update the conversation_tree and other necessary states
                # ! In the future conversation tree could be a tree structure
                self.current_branch = 0
                self.conversation_tree = [self.current_conversation]
                self.previous_conversation = self.current_conversation

    def rerun_chat_from_index(self, idx):
        new_messages = self.messages[:idx+1]
        new_conversation = copy.deepcopy(self.current_conversation)
        new_conversation.messages = [Message(msg.role, msg.content) for msg in new_messages]
        self.conversation_tree.append(new_conversation)
        self.current_branch = len(self.conversation_tree) - 1

    def edit_message_in_session(self):
        with st.expander("Edit a message"):
            c1, c2, c3 = st.columns(3)
            self.current_branch = c1.number_input(
                "Conversation Tree",
                min_value=0,
                max_value=len(self.conversation_tree) - 1,
                value=len(self.conversation_tree) - 1
            )
            self.messages = self.conversation_tree[self.current_branch].messages
            msg_idx_to_edit = c2.number_input(
                "index of message to edit",
                min_value=0,
                max_value=len(self.messages) - 1,
                value=0
            )
            if c3.button("Rerun from message index", on_click=self.rerun_chat_from_index, args=(msg_idx_to_edit,)):
                st.rerun()
            self.current_conversation = self.conversation_tree[self.current_branch]
            self.messages = [msg for msg in self.current_conversation.messages]
            msg_to_edit = self.messages[msg_idx_to_edit].content
            msg_to_edit = st.text_area("edit message", value=msg_to_edit)
            self.messages[msg_idx_to_edit].content = msg_to_edit

    def clear_chat_history(self):
        self.messages = self.__class__.DEFAULT_CONVERSATION.messages
        pass

    def display_chat(self):
        """Display the chat interface and handle chat logic."""
        st.title(f"💬 Chat with {self.agent_name}")
        # ... logic
        self.edit_message_in_session()
        self.current_conversation = self.conversation_tree[self.current_branch]
        self.messages = self.current_conversation.messages

        # Display or clear chat messages
        for message in self.messages:
            with st.chat_message(message.role):
                st.write(message.content)
#               st.write(
    #               message["content"],
    #               st.number_input(uuid.uuid1().__str__(), step=1, label_visibility="hidden")
    #           )
        if prompt := st.chat_input("What is up?"):
            if self.messages and self.messages[-1].role == "user":
                # Merge with the previous user message
                self.messages[-1].content += "\n\n" + prompt
                with st.chat_message("user"):
                    st.markdown(self.messages[-1].content)
            else:
                # Append as a new message
                self.messages.append(Message("user", prompt))
                with st.chat_message("user"):
                    st.markdown(prompt)

            self.generate_assistant_response()

    def generate_assistant_response(self):
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response_chunk in openai_client.chat.completions.create(
                model=self.selected_model,
                messages=[message.to_dict() for message in self.messages],
                stream=True,
            ):
                # Check if content is not None before concatenating
                content = response_chunk.choices[0].delta.content if response_chunk.choices[0].delta.content is not NoneType else ""
                full_response += (str(content) if content is not None else '')
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        self.messages.append(Message("assistant", full_response))
        self.current_conversation.messages = self.messages
        st.rerun()

    def run(self):
        """Main function to run the chatbot."""
        self.display_sidebar()
        self.display_chat()


repos = justai.frameworks_and_drivers.database_sidebar.database_sidebar()
openai_client = justai.frameworks_and_drivers.llm_sidebar.llm_sidebar()
user_use_cases = UserUseCases(repos["user"])
agent_use_cases = AgentUseCases(repos["agent"], repos["backup"], repos["conversation"])
conversation_use_cases = ConversationUseCases(repos["agent"], repos["conversation"], repos["backup"])

# In the main execution:
if "chatbot" not in st.session_state:
    st.session_state.chatbot = StreamlitChatbot(user_use_cases, agent_use_cases, conversation_use_cases, openai_client)

st.session_state.chatbot.run()

feedback_use_cases = FeedbackUseCases(repos["feedback"])
feedback_management_dashboard = FeedbackManagementDashboard(feedback_use_cases, user_use_cases)
