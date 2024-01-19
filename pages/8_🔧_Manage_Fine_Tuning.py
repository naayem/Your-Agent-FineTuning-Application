import streamlit as st
import pandas as pd
from io import StringIO

import os
import locale

from streamlit_sortables import sort_items
import justai

locale.getpreferredencoding = lambda: "UTF-8"

# App title
st.set_page_config(page_title="JYA OpenAI Fine-Tuning 👁️", layout="wide")

########################################################################################################################
# SIDEBAR
########################################################################################################################
openai_client = justai.frameworks_and_drivers.llm_sidebar.llm_sidebar()

########################################################################################################################
# Fine-Tuning
########################################################################################################################
'''
# Fine-Tuning
'''

with st.expander("Key Features"):
    '''
    ### Key Features & How to Use Them:

    1. **File Management Section:**
        - **Local Datasets:** View a list of datasets available on your local machine, ready for upload and fine-tuning.
        - **OpenAI Files:** Check the files you've published on OpenAI, complete with file names and unique IDs.
        - **File Details:** A concise list of files with IDs helps you keep track of your resources on OpenAI.
    2. **Publishing Files:**
        -**Upload Files:** Easily publish your local files to OpenAI by selecting from the dropdown menu and clicking 'Create a File on OpenAI'.
        -**Delete Files:** Maintain your workspace by selecting and removing unwanted files from OpenAI.
    3. **Fine-Tuning Jobs Management:**
        - **Job Overview:** Monitor your fine-tuning jobs with a summary including model details and job IDs.
        - **Create Jobs:** Start new fine-tuning jobs by providing the necessary file IDs and selecting your model.
        - **Retrieve & Delete Jobs:** Look up details of existing jobs or remove them using their Job IDs.
    4. **Metrics and Visuals:**
        - **Metrics Retrieval:** For in-depth analysis, input the metrics file ID to display fine-tuning metrics.
        - **Visual Insights:** The Metrics Visualizer graphically represents your model's performance over time, providing clarity on training and validation metrics.
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
file_objects = openai_client.files.list(purpose='fine-tune').data
file_dicts = [file_object.__dict__ for file_object in file_objects]
col2.json(file_dicts, expanded=False)

col3.write("**The list of files in the response {'id','name'}:**")
returned_dic_of_files = openai_client.files.list()
list_of_files = [{'filename': file['filename'], 'id': file["id"]}for file in file_dicts]
files_openai_items = [f"{file['filename']} - id: file-...{file['id'][-4:-1]}" for file in file_dicts]
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
        st.json(openai_client.files.create(
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
            st.json(openai_client.files.delete(file['id']), expanded=False)


# openai.File.retrieve("file-CY0FPBluqbVcoHmuGLI80lqx")


'''
## Manage Jobs for Fine-Tuning
'''

col1, col2 = st.columns(2)

list_jobs = openai_client.fine_tuning.jobs.list(limit=10).data
jobs_dicts = [job_object.__dict__ for job_object in list_jobs]
list_jobs_filtered = [{'fine_tuned_model': job['fine_tuned_model'], 'id': job["id"]}for job in jobs_dicts]
#jobs_openai_items = [f"{file['filename']} - id: file-...{file['id'][-4:-1]}" for file in file_dicts]

col1.write('**List of Jobs published on OpenAI**')
col1.json(list_jobs_filtered, expanded=False)
col1.caption("Note to dev: remember the limit parameter is used (10)to avoid long lists")

col2.write('**List of files published on OpenAI**')

col2.write(" The list of files in the response {'id','name'}: ")
file_objects = openai_client.files.list(purpose="fine-tune-results").data
file_dicts = [file_object.__dict__ for file_object in file_objects]
list_of_files = [{'filename': file['filename'], 'id': file["id"]}for file in file_dicts]
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
            openai_client.fine_tuning.jobs.create(
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
            openai_client.fine_tuning.jobs.retrieve(job_id),
            expanded=False
            )

with col3.form("delete_ft_job"):
    job_id = st.text_input("Job ID").strip('"')

    # Every form must have a submit button.
    submitted = st.form_submit_button("Delete Fine-Tuning Job")
    if submitted:
        st.write("job_id: ", job_id)
        st.json(
            openai_client.fine_tuning.jobs.cancel(job_id),
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

        list_events_all_data = openai_client.fine_tuning.jobs.list_events(id=job_id, limit=limit_events)
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
            openai_client.models.delete(job_id)
            )


def get_step_metrics(file_id):
    content = openai_client.files.content(file_id).content

    # Save the raw content to a local file
    with open('data/metrics/test.csv', 'wb') as file:
        file.write(content)

    eval_result = StringIO(content.decode())
    df = pd.read_csv(eval_result, sep=",")
    return df


with col3.form("read_metrics"):
    m_file_id = st.text_input("metrics file ID", value="file-CAfAF4k9SAXeR9uUKcW6zKtw").strip('"')

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
