import streamlit as st

import locale

from justai.data_openai_analysis import data_loading_openft, estimate_cost, validate_format
from justai.data_openai_analysis import count_tokens_and_data_warnings
from justai.dataset import format_dataframe_for_display, iio_jsonl_formatting
from justai.dataset import import_gen_dataset, template_message_format_display
from justai.old.cells_content import display_code_generation_dataset

locale.getpreferredencoding = lambda: "UTF-8"


########################################################################################################################
# Dataset
########################################################################################################################
'''
# Fine Tuning Experimentation
## Import The Code Generation Dataset 📋
'''
display_code_generation_dataset()

code_generation_dataframe = import_gen_dataset()


num_df_rows = st.slider("Select number of rows to display:",
                        1,
                        len(code_generation_dataframe))
st.write(code_generation_dataframe.head(num_df_rows))


'''
## Writing the template message format
'''
template_message_format = template_message_format_display()

'''
## Let's now format the dataset into the correct format for the API
'''
# File to write the JSONL output
# format instruction- input - output dataframe into JSONL
formatted_file = iio_jsonl_formatting(code_generation_dataframe,
                                      template_message_format)

ds_tr_df_for_display = format_dataframe_for_display(path='data/openai_ready/output_train.jsonl')
ds_va_df_for_display = format_dataframe_for_display(path="data/openai_ready/output_valid.jsonl")
ds_ts_df_for_display = format_dataframe_for_display(path="data/openai_ready/output_test.jsonl")

num_formatted_df_rows = st.slider("Select number of rows to display:",
                                  1,
                                  len(ds_tr_df_for_display))
st.write(code_generation_dataframe.head(num_formatted_df_rows))

'''
## Data Preparation and Analysis
'''

'''
### Training Dataset
'''

pre_validation_dataset_tr = data_loading_openft("output_train.jsonl")
validate_format(pre_validation_dataset_tr)
pre_val_convo_lens_tr = count_tokens_and_data_warnings(pre_validation_dataset_tr)
estimate_cost(pre_validation_dataset_tr, pre_val_convo_lens_tr)

'''
### Validation Dataset
'''
pre_validation_dataset_va = data_loading_openft("output_valid.jsonl")
validate_format(pre_validation_dataset_va)
pre_val_convo_lens_va = count_tokens_and_data_warnings(pre_validation_dataset_va)
estimate_cost(pre_validation_dataset_va, pre_val_convo_lens_va)

'''
### Test Dataset
'''

pre_validation_dataset_ts = data_loading_openft("output_test.jsonl")
validate_format(pre_validation_dataset_ts)
pre_val_convo_lens_ts = count_tokens_and_data_warnings(pre_validation_dataset_ts)
estimate_cost(pre_validation_dataset_ts, pre_val_convo_lens_ts)