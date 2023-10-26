import streamlit as st

import locale

from justai.data_openai_analysis import data_loading_openft, estimate_cost, validate_format
from justai.data_openai_analysis import count_tokens_and_data_warnings
from justai.dataset import format_dataframe_for_display, iio_jsonl_formatting, messages_jsonl_formatting
from justai.dataset import import_gen_dataset, template_message_format_display
import justai
from justai.use_cases.agent_use_cases import AgentUseCases
from justai.use_cases.conversation_use_cases import ConversationUseCases

locale.getpreferredencoding = lambda: "UTF-8"

########################################################################################################################
# SIDEBAR
########################################################################################################################
repos = justai.frameworks_and_drivers.database_sidebar.database_sidebar()

if not repos:
    st.warning("Please configure the database connection first.")

agent_use_cases = AgentUseCases(repos["agent"], repos["backup"], repos["conversation"])
conversation_use_cases = ConversationUseCases(repos["agent"], repos["conversation"], repos["backup"])


########################################################################################################################
# Dataset
########################################################################################################################
'''
# Import and Prepare a Dataset
## I- Import a dataset from a link 📋
'''
# Display Agents
st.subheader("Agents")
agents = agent_use_cases.get_all()
agent_names = [agent.name for agent in agents]
# Convert list of Agent objects to list of dictionaries
agents_data = [agent.to_dict() for agent in agents]
st.dataframe(agents_data)
agent_name = st.selectbox("Select an agent", agent_names)

dataset_agent_dataframe = import_gen_dataset(conversation_use_cases, agent_name)


num_df_rows = st.slider("Select number of rows to display:",
                        1,
                        len(dataset_agent_dataframe),
                        min(5, len(dataset_agent_dataframe)))
dataset_agent_dataframe_display = dataset_agent_dataframe.copy()
dataset_agent_dataframe_display['messages'] = dataset_agent_dataframe_display['messages'].apply(str)

st.write(dataset_agent_dataframe_display.head(num_df_rows))


'''
## II- Writing the template message format
'''
template_message_format = template_message_format_display()

'''
## III- Let's now format the dataset into the correct format for the API
'''
# File to write the JSONL output
# format instruction- input - output dataframe into JSONL
column_list = dataset_agent_dataframe.columns.tolist()
formats = ["'instruction', 'input', and 'output'", "Messages"]
selected_format = st.selectbox("Select the format of your dataset", formats, index=1)

if selected_format == formats[0]:
    with st.form("Format the dataset for fitting into the API"):
        st.write("Assuming you have a DataFrame 'df' with columns 'instruction', 'input', and 'output'")

        # Get column names for user and assistant messages from the user
        user_message_columns = st.multiselect(
            "Select columns for User Message",
            dataset_agent_dataframe.columns,
            column_list,
            key="user_cols"
        )

        assistant_message_columns = st.multiselect(
            "Select columns for Assistant Message",
            dataset_agent_dataframe.columns,
            column_list,
            key="assistant_cols"
        )

        # Every form must have a submit button.
        submitted = st.form_submit_button("Format the dataset for fitting into the API")
        if submitted:
            formatted_file = iio_jsonl_formatting(
                dataset_agent_dataframe,
                template_message_format,
                user_message_columns,
                assistant_message_columns
                )

            ds_tr_df_for_display = format_dataframe_for_display(path='data/openai_ready/output_train.jsonl')
            ds_va_df_for_display = format_dataframe_for_display(path="data/openai_ready/output_valid.jsonl")
            ds_ts_df_for_display = format_dataframe_for_display(path="data/openai_ready/output_test.jsonl")

            num_formatted_df_rows = st.slider(
                "Select number of rows to display:",
                1,
                len(ds_tr_df_for_display)
                )
            st.write(ds_tr_df_for_display.head(num_formatted_df_rows))
            st.write(ds_va_df_for_display.head(num_formatted_df_rows))
            st.write(ds_ts_df_for_display.head(num_formatted_df_rows))

if selected_format == formats[1]:
    with st.form("Format the dataset for fitting into the API"):
        '''
        Assuming you have a Messages format
        '''

        # Get column names for user and assistant messages from the user
        messages_columns = st.multiselect(
            "Select the Messages column",
            dataset_agent_dataframe.columns,
            key="Messages_cols"
        )

        # Every form must have a submit button.
        submitted = st.form_submit_button("Format the dataset for fitting into the API")
        if submitted:
            formatted_file = messages_jsonl_formatting(
                dataset_agent_dataframe,
                messages_columns
                )

ds_tr_df_for_display = format_dataframe_for_display(path='data/openai_ready/output_train.jsonl')
ds_va_df_for_display = format_dataframe_for_display(path="data/openai_ready/output_valid.jsonl")
ds_ts_df_for_display = format_dataframe_for_display(path="data/openai_ready/output_test.jsonl")

st.write(len(ds_tr_df_for_display))
num_formatted_df_rows = st.slider(
    "Select number of rows to display:",
    1,
    len(ds_tr_df_for_display),
    min(5, len(ds_tr_df_for_display))
    )
st.dataframe(ds_tr_df_for_display.head(num_formatted_df_rows), use_container_width=True)
st.dataframe(ds_va_df_for_display.head(num_formatted_df_rows), use_container_width=True)
st.dataframe(ds_ts_df_for_display.head(num_formatted_df_rows), use_container_width=True)

'''
## IV-Data Preparation and Analysis
'''

cost_per_1k_tokens_default = 0.0080
col1, col2 = st.columns(2)
n_epochs_manual = col1.number_input(
    "Number of epochs",
    min_value=1,
    max_value=99999999,
    value=1
    )
cost_per_1k_tokens = col2.number_input(
    "Cost per 1k tokens",
    min_value=0.0001,
    max_value=0.9999,
    value=cost_per_1k_tokens_default,
    step=0.0001,
    format="%.4f"
    )

st.caption("An epoch is a single pass through the entire dataset. ")
st.divider()

'''
### 1. Training Dataset
'''

pre_validation_dataset_tr = data_loading_openft("data/openai_ready/output_train.jsonl")
format_errors_tr = validate_format(pre_validation_dataset_tr)
if pre_validation_dataset_tr:
    pre_val_convo_lens_tr = count_tokens_and_data_warnings(pre_validation_dataset_tr)
    estimate_cost(pre_validation_dataset_tr, pre_val_convo_lens_tr, n_epochs_manual, cost_per_1k_tokens)
else:
    st.metric("Training Dataset", "Empty")
st.divider()
'''
### 2. Validation Dataset
'''

pre_validation_dataset_va = data_loading_openft("data/openai_ready/output_valid.jsonl")
format_errors_val = validate_format(pre_validation_dataset_va)
if format_errors_val:
    st.write("Found errors:")
    for k, v in format_errors_val.items():
        st.write(f"{k}: {v}")
else:
    st.metric("Format Errors", "0")
if pre_validation_dataset_va:
    pre_val_convo_lens_va = count_tokens_and_data_warnings(pre_validation_dataset_va)
    estimate_cost(pre_validation_dataset_va, pre_val_convo_lens_va, n_epochs_manual, cost_per_1k_tokens)
else:
    st.metric("Validation Dataset", "Empty")
st.divider()
'''
### 3. Test Dataset
'''

pre_validation_dataset_ts = data_loading_openft("data/openai_ready/output_test.jsonl")
format_errors_ts = validate_format(pre_validation_dataset_ts)
if pre_validation_dataset_ts:
    pre_val_convo_lens_ts = count_tokens_and_data_warnings(pre_validation_dataset_ts)
    estimate_cost(pre_validation_dataset_ts, pre_val_convo_lens_ts, n_epochs_manual, cost_per_1k_tokens)
else:
    st.metric("Test Dataset", "Empty")
st.divider()
