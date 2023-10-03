import streamlit as st

import locale

from justai.data_openai_analysis import data_loading_openft, estimate_cost, validate_format
from justai.data_openai_analysis import count_tokens_and_data_warnings
from justai.dataset import format_dataframe_for_display, iio_jsonl_formatting
from justai.dataset import import_gen_dataset, template_message_format_display
from justai.old.cells_content import display_code_generation_dataset

locale.getpreferredencoding = lambda: "UTF-8"

########################################################################################################################
# SIDEBAR
########################################################################################################################
with st.sidebar:
    st.title(' JAW OpenAI Fine-Tuning 👁️')
    st.button("Reset", type="primary")


########################################################################################################################
# Dataset
########################################################################################################################
'''
# Import and Prepare a Dataset
## I- Import a dataset from a link 📋
'''
display_code_generation_dataset()

st.text_input(
    "Enter the link to the dataset",
    value="https://raw.githubusercontent.com/sahil280114/codealpaca/master/data/code_alpaca_20k.json"
    )
code_generation_dataframe = import_gen_dataset()


num_df_rows = st.slider("Select number of rows to display:",
                        1,
                        len(code_generation_dataframe))
st.write(code_generation_dataframe.head(num_df_rows))


'''
## II- Writing the template message format
'''
template_message_format = template_message_format_display()

'''
## III- Let's now format the dataset into the correct format for the API
'''
# File to write the JSONL output
# format instruction- input - output dataframe into JSONL

with st.form("Format the dataset for fitting into the API"):
    '''
    Assuming you have a DataFrame 'df' with columns 'instruction', 'input', and 'output'
    '''
    user_message_columns = ['instruction', 'input']
    assistant_message_columns = ['output']

    # Get column names for user and assistant messages from the user
    user_message_columns = st.multiselect(
        "Select columns for User Message",
        code_generation_dataframe.columns,
        user_message_columns,
        key="user_cols"
    )

    assistant_message_columns = st.multiselect(
        "Select columns for Assistant Message",
        code_generation_dataframe.columns,
        assistant_message_columns,
        key="assistant_cols"
    )

    # Every form must have a submit button.
    submitted = st.form_submit_button("Format the dataset for fitting into the API")
    if submitted:
        formatted_file = iio_jsonl_formatting(
            code_generation_dataframe,
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
pre_val_convo_lens_tr = count_tokens_and_data_warnings(pre_validation_dataset_tr)
estimate_cost(pre_validation_dataset_tr, pre_val_convo_lens_tr, n_epochs_manual, cost_per_1k_tokens)
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
pre_val_convo_lens_va = count_tokens_and_data_warnings(pre_validation_dataset_va)
estimate_cost(pre_validation_dataset_va, pre_val_convo_lens_va, n_epochs_manual, cost_per_1k_tokens)
st.divider()
'''
### 3. Test Dataset
'''

pre_validation_dataset_ts = data_loading_openft("data/openai_ready/output_test.jsonl")
validate_format(pre_validation_dataset_ts)
pre_val_convo_lens_ts = count_tokens_and_data_warnings(pre_validation_dataset_ts)
estimate_cost(pre_validation_dataset_ts, pre_val_convo_lens_ts, n_epochs_manual, cost_per_1k_tokens)
st.divider()
