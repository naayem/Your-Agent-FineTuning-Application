import streamlit as st
from typing import Union, Dict

from justai.frameworks_and_drivers.mongo_repositories import MongoAgentRepository, MongoBackupRepository
from justai.frameworks_and_drivers.mongo_repositories import MongoConversationRepository
from justai.interface_adapters.conversational_repository_interface import IAgentRepository, IBackupRepository
from justai.interface_adapters.conversational_repository_interface import IConversationRepository

REPOSITORIES = {
    'mongodb': {
        'agent': MongoAgentRepository,
        'conversation': MongoConversationRepository,
        'backup': MongoBackupRepository
    }
}

SUCCESS_CONDITIONS = {
    'mongodb': lambda x: x.startswith("mongodb+srv")
}


def init_repositories(
    database_type,
    connection_link
) -> Dict[str, Union[IAgentRepository, IConversationRepository, IBackupRepository]]:
    repo_classes = REPOSITORIES.get(database_type)
    if not repo_classes:
        raise ValueError(f"Unsupported database type: {database_type}")

    repos = {}
    for repo_key, repo_class in repo_classes.items():
        repos[repo_key] = repo_class(connection_link)
    return repos


def database_sidebar() -> Union[Dict[str, Union[IAgentRepository, IConversationRepository, IBackupRepository]], None]:
    """
    Renders the Streamlit sidebar for setting up and updating database connections.

    Returns:
    - db_client (MongoClient or None): Returns a MongoClient if connection is successful, None otherwise.
    """
    repos = None
    with st.sidebar:
        st.title('Database Connection Sidebar 👁️')
        st.button("Reset")

        if 'repos' in st.session_state and not st.session_state.get('update_connection', False):
            st.success('Connected to database!')
            if st.button("Update Connection"):
                st.session_state.update_connection = True
            return st.session_state.repos

        db_type = st.selectbox('Select Database', ['mongodb', '...others'])
        secret_key = f"{db_type.upper()}_SRV"

        if secret_key in st.secrets:
            connection_link = st.secrets[secret_key]
            try:
                repos = init_repositories(db_type, connection_link)
                st.success(f'{db_type.capitalize()} repositories initialized!', icon='✅')

                st.session_state.repos = repos
                st.session_state.update_connection = False
                return repos
            except Exception as e:
                st.error(f'Error initializing repositories for {db_type}: {e}')
        else:
            connection_link = st.text_input(
                f"Enter your {db_type.capitalize()} connection link",
                value=""
            ).strip('"')
            if not connection_link:
                st.warning(f'Please enter your {db_type.capitalize()} link!', icon='⚠️')
            if (SUCCESS_CONDITIONS[db_type](connection_link)):
                st.success('Proceed to develop your dataset!', icon='👉')
            else:
                st.warning(f'Please enter your {db_type.capitalize()} link!', icon='⚠️')

        if st.button("Reset_1"):
            if 'db_client' in st.session_state:
                del st.session_state['db_client']
            if 'update_connection' in st.session_state:
                del st.session_state['update_connection']

    if repos:
        return repos
    else:
        return None
