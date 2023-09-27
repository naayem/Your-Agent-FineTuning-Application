import streamlit as st
import openai
import pandas as pd
from io import StringIO

import os
import locale

locale.getpreferredencoding = lambda: "UTF-8"

# App title
st.set_page_config(page_title="JAW OpenAI FineTuning 👁️", layout="wide")

########################################################################################################################
# SIDEBAR
########################################################################################################################
with st.sidebar:
    st.title(' JAW Llama2 Chatbot 👁️')
    if 'OPENAI_TOKEN' in st.secrets:
        openai_api_key = st.secrets['OPENAI_TOKEN']
        openai.api_key = openai_api_key
        st.success('OpenAI API key provided!', icon='✅')
    else:
        openai_api_key = st.text_input(
            "Enter an OpenAI API token ",
            value="",
            type="password")
        if not (openai_api_key.startswith('sk-')
                and len(openai_api_key) == 51):
            openai_api_key = None
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to explore Fine Tuning!', icon='👉')

    st.button("Reset", type="primary")

########################################################################################################################
# Fine Tuning
########################################################################################################################
'''
# Fine Tuning
'''

'''
## Manage files for Fine Tuning
'''
col1, col2 = st.columns(2)
col1.write('### The list of available datasets locally: ')
list_of_available_datasets = [file for file in os.listdir("data/openai_ready")]
col1.write(list_of_available_datasets)
col1.write('Num of datasets: ')
col1.write(len(list_of_available_datasets))

col2.write('### List of files published on OpenAI')
col2.write('The entire API response:')
col2.write(openai.File.list())

col2.write(" The list of files in the response {'id','name'}: ")
returned_dic_of_files = openai.File.list()
list_of_files = [{'id': file["id"], 'filename': file['filename']}for file in returned_dic_of_files["data"]]
col2.write(list_of_files)
col2.write('Num of datasets: ')
col2.write(len(list_of_files))

'''
### Publish a file on OpenAI
'''
with st.form("create_file_openai"):
    dataset_to_submit_to_openai = st.selectbox("Select a file", list_of_available_datasets)
    # Every form must have a submit button.
    submitted = st.form_submit_button("Create a File on OpenAI")
    if submitted:
        st.write('File submitted: ', dataset_to_submit_to_openai)
        st.write('Response of openai.File.Create: ')
        st.write(openai.File.create(
            file=open("data/openai_ready/"+dataset_to_submit_to_openai, "rb"),
            purpose='fine-tune',
            user_provided_filename=dataset_to_submit_to_openai
        ))
'''
### Delete files on OpenAI
'''
with st.form("delete_form"):
    st.write("Inside the form")
    selected_file_to_delete = st.multiselect("Select files to delete", list_of_files)

    # Every form must have a submit button.
    submitted = st.form_submit_button("Delete the selected files")
    if submitted:
        for file in selected_file_to_delete:
            st.write(openai.File.delete(file['id']))


# openai.File.retrieve("file-CY0FPBluqbVcoHmuGLI80lqx")


'''
## Manage Jobs for Fine Tuning
'''

col1, col2 = st.columns(2)

col1.write('### List of Jobs published on OpenAI')
# List 10 fine-tuning jobs
if col1.checkbox("List Fine Tuning Jobs", value=True):
    col1.write(openai.FineTuningJob.list(limit=10))

col2.write('### List of files published on OpenAI')

col2.write(" The list of files in the response {'id','name'}: ")
returned_dic_of_files = openai.File.list()
list_of_files = [{'id': file["id"], 'filename': file['filename']}for file in returned_dic_of_files["data"]]
col2.write(list_of_files)


with st.form("create_fine_tuning_job"):
    tr_file_id = st.text_input("Training File ID")
    val_file_id = st.text_input("Validation File ID")
    selected_model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-3.5-turbo"])

    # Every form must have a submit button.
    submitted = st.form_submit_button("Create Fine Tuning Job")
    if submitted:
        st.write("tr_file_id: ", tr_file_id, " val_file_id: ", val_file_id, " selected_model: ", selected_model)
        st.write(
            openai.FineTuningJob.create(
                training_file=tr_file_id,
                validation_file=val_file_id,
                model="gpt-3.5-turbo"
                )
            )

with st.form("retrieve_ft_job"):
    job_id = st.text_input("Job ID")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Retrieve Fine Tuning Job")
    if submitted:
        st.write("job_id: ", job_id)
        st.write(
            openai.FineTuningJob.retrieve(job_id)
            )

with st.form("delete_ft_job"):
    job_id = st.text_input("Job ID")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Delete Fine Tuning Job")
    if submitted:
        st.write("job_id: ", job_id)
        st.write(
            openai.FineTuningJob.cancel(job_id)
            )

with st.form("events_ft_job"):
    job_id = st.text_input("Job ID")
    limit_events = st.number_input("Limit number of events", value=10)

    # Every form must have a submit button.
    submitted = st.form_submit_button("List a Fine Tuning Job events")
    if submitted:
        st.write("job_id: ", job_id)
        st.write(
            openai.FineTuningJob.list_events(id=job_id, limit=limit_events)
            )

with st.form("delete_ft_model"):
    model_id = st.text_input("Model ID")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Delete Fine Tuning Model")
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


with st.form("read_metrics"):
    m_file_id = st.text_input("metrics file ID")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Display Fine Tuning metrics")
    if submitted:
        st.write("m_file_id: ", m_file_id)
        metrics_df = get_step_metrics(m_file_id)
        st.write(metrics_df)

        st.title("Metrics Visualizer")
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
