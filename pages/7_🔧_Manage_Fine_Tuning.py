import streamlit as st
import openai
import pandas as pd
from io import StringIO

import os
import locale

from streamlit_sortables import sort_items

locale.getpreferredencoding = lambda: "UTF-8"

# App title
st.set_page_config(page_title="JAW OpenAI Fine-Tuning 👁️", layout="wide")

########################################################################################################################
# SIDEBAR
########################################################################################################################
with st.sidebar:
    st.title(' JAW OpenAI Fine-Tuning 👁️')
    if 'OPENAI_TOKEN' in st.secrets:
        openai_api_key = st.secrets['OPENAI_TOKEN']
        openai.api_key = openai_api_key
        st.success('OpenAI API key provided!', icon='✅')
    else:
        openai_api_key = st.text_input(
            "Enter an OpenAI API token ",
            value="",
            type="password").strip('"')
        if not (openai_api_key.startswith('sk-')
                and len(openai_api_key) == 51):
            openai_api_key = None
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to explore Fine-Tuning!', icon='👉')

    st.button("Reset", type="primary")

########################################################################################################################
# Fine-Tuning
########################################################################################################################
'''
# Fine-Tuning
'''

'''
## Manage files for Fine-Tuning
'''

col1, col2, col3 = st.columns(3)
col1.write('**The list of available datasets locally:**')
list_of_available_datasets = [file for file in os.listdir("data/openai_ready")]
col1.write(f'Num of datasets:`{len(list_of_available_datasets)}` ')
col1.json(list_of_available_datasets, expanded=False)


col2.write(' **List of files published on OpenAI**')
col2.write('The entire API response:')
col2.json(openai.File.list(), expanded=False)

col3.write("**The list of files in the response {'id','name'}:**")
returned_dic_of_files = openai.File.list()
list_of_files = [{'filename': file['filename'], 'id': file["id"]}for file in returned_dic_of_files["data"]]
files_openai_items = [f"{file['filename']} - id: file-...{file['id'][-4:-1]}" for file in returned_dic_of_files["data"]]
col3.write(f'Num of files:`{len(list_of_files)}` ')
col3.json(list_of_files, expanded=False)

files_items = [
    {'header': 'Files on local machine', 'items': list_of_available_datasets},
    {'header': 'Files on OpenAI platform',  'items': files_openai_items}
]

sorted_items = sort_items(files_items, multi_containers=True, direction='vertical')

'''
### Publish a file on OpenAI
'''
col1, col2, col3 = st.columns(3)
with col1.form("create_file_openai"):
    dataset_to_submit_to_openai = st.selectbox("Select a file", list_of_available_datasets)
    # Every form must have a submit button.
    submitted = st.form_submit_button("Create a File on OpenAI")
    if submitted:
        st.write('File submitted: ', dataset_to_submit_to_openai)
        st.write('Response of openai.File.Create: ')
        st.json(openai.File.create(
            file=open("data/openai_ready/"+dataset_to_submit_to_openai, "rb"),
            purpose='fine-tune',
            user_provided_filename=dataset_to_submit_to_openai
            ),
            expanded=False
        )
'''
### Delete files on OpenAI
'''
with col2.form("delete_form"):
    selected_file_to_delete = st.multiselect("Select files to delete", list_of_files)

    # Every form must have a submit button.
    submitted = st.form_submit_button("Delete the selected files")
    if submitted:
        for file in selected_file_to_delete:
            st.json(openai.File.delete(file['id']), expanded=False)


# openai.File.retrieve("file-CY0FPBluqbVcoHmuGLI80lqx")


'''
## Manage Jobs for Fine-Tuning
'''

col1, col2 = st.columns(2)

col1.write('**List of Jobs published on OpenAI**')
col1.json(openai.FineTuningJob.list(limit=10), expanded=False)
col1.caption("Note to dev: remember the limit parameter is used (10)to avoid long lists")

col2.write('**List of files published on OpenAI**')

col2.write(" The list of files in the response {'id','name'}: ")
returned_dic_of_files = openai.File.list()
list_of_files = [{'filename': file['filename'], 'id': file["id"]}for file in returned_dic_of_files["data"]]
col2.json(list_of_files, expanded=False)

col1, col2, col3 = st.columns(3)
with col1.form("create_fine_tuning_job"):
    tr_file_id = st.text_input("Training File ID").strip('"')
    st.write(tr_file_id)
    val_file_id = st.text_input("Validation File ID").strip('"')
    selected_model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-3.5-turbo"])

    # Every form must have a submit button.
    submitted = st.form_submit_button("Create Fine-Tuning Job")
    if submitted:
        st.write("tr_file_id: ", tr_file_id, " val_file_id: ", val_file_id, " selected_model: ", selected_model)
        st.write(
            openai.FineTuningJob.create(
                training_file=tr_file_id,
                validation_file=val_file_id,
                model="gpt-3.5-turbo"
                )
            )

with col2.form("retrieve_ft_job"):
    job_id = st.text_input("Job ID").strip('"')

    # Every form must have a submit button.
    submitted = st.form_submit_button("Retrieve Fine-Tuning Job")
    if submitted:
        st.write("job_id: ", job_id)
        st.json(
            openai.FineTuningJob.retrieve(job_id),
            expanded=False
            )

with col3.form("delete_ft_job"):
    job_id = st.text_input("Job ID").strip('"')

    # Every form must have a submit button.
    submitted = st.form_submit_button("Delete Fine-Tuning Job")
    if submitted:
        st.write("job_id: ", job_id)
        st.json(
            openai.FineTuningJob.cancel(job_id),
            expanded=False
            )


# Function to display events as a DataFrame
def display_events_as_dataframe(event_data_response, event_features):
    event_dict = {}

    for feature in event_features:
        if feature['value']:
            column_label = feature['feature_label']
            st.write([event[column_label] for event in event_data_response["data"]])
            event_dict.update({column_label: [event[column_label] for event in event_data_response["data"]]})

    st.write(event_dict)
    df = pd.DataFrame(event_dict)
    return df


with col1.form("events_ft_job"):
    job_id = st.text_input("Job ID").strip('"')
    limit_events = st.number_input("Limit number of events", value=10)

    columns_l_e = st.columns(4)
    event_features = [
        {"feature_label": "id", "value": False, "column": columns_l_e[0]},
        {"feature_label": "created_at", "value": False, "column": columns_l_e[0]},
        {"feature_label": "level", "value": False, "column": columns_l_e[1]},
        {"feature_label": "message", "value": False, "column": columns_l_e[1]},
        {"feature_label": "data", "value": False, "column": columns_l_e[2]},
        {"feature_label": "type", "value": False, "column": columns_l_e[2]}
        ]

    for ev_feat in event_features:
        ev_feat["value"] = ev_feat["column"].checkbox(ev_feat["feature_label"])

    # Every form must have a submit button.
    submitted = st.form_submit_button("List a Fine-Tuning Job events")

    if submitted:
        st.write("job_id: ", job_id)

        list_events_all_data = openai.FineTuningJob.list_events(id=job_id, limit=limit_events)
        # Display DataFrame based on selected features
        with st.expander("List of events, Choose data to display"):
            df_list_events = display_events_as_dataframe(list_events_all_data, event_features)
            st.write(df_list_events)

with col2.form("delete_ft_model"):
    model_id = st.text_input("Model ID").strip('"')

    # Every form must have a submit button.
    submitted = st.form_submit_button("Delete Fine-Tuning Model")
    if submitted:
        st.write("model_id: ", model_id)
        st.write(
            openai.Model.delete(job_id)
            )


def get_step_metrics(file_id):
    content = openai.File.download(file_id)

    # Save the raw content to a local file
    with open('data/metrics/test.csv', 'wb') as file:
        file.write(content)

    eval_result = StringIO(content.decode())
    df = pd.read_csv(eval_result, sep=",")
    return df


with col3.form("read_metrics"):
    m_file_id = st.text_input("metrics file ID").strip('"')

    # Every form must have a submit button.
    submitted = st.form_submit_button("Display Fine-Tuning metrics")
    if submitted:
        st.write("m_file_id: ", m_file_id)
        metrics_df = get_step_metrics(m_file_id)
        with st.expander("Metrics DataFrame", expanded=False):
            st.write(metrics_df)

        st.title("Metrics Visualizer")
        with st.expander("Metrics Visualizer", expanded=True):
            st.write("Below is the visualization of metrics over steps:")
            metrics_df = metrics_df.fillna(method="ffill")
            st.line_chart(
                metrics_df, x="step", y=["train_loss", "train_accuracy", "valid_loss", "valid_mean_token_accuracy"]
            )
            validation_filtered_metrics_df = metrics_df[metrics_df['step'] % 100 == 0]
            st.line_chart(
                validation_filtered_metrics_df, x="step", y=["valid_loss", "valid_mean_token_accuracy"]
            )
            # Handling NaNs
