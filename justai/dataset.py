import json
import streamlit as st
import numpy as np
import pandas as pd


@st.cache_data
def import_gen_dataset():
    progress_bar = st.progress(0, "Processing dataset")
    status_text = st.empty()

    status_text.text("Initializing seed...")
    np.random.seed(123)
    progress_bar.progress(10, "Processing dataset")
    status_text.text("Initialized seed...")

    status_text.text("loading dataframe from link...")
    df = pd.read_json("https://raw.githubusercontent.com/sahil280114/codealpaca/master/data/code_alpaca_20k.json")
    progress_bar.progress(60, "Processing dataset")
    status_text.text("Loaded dataset...")

    # We're going to create a new column called `split` where:
    # 90% will be assigned a value of 0 -> train set
    # 5% will be assigned a value of 1 -> validation set
    # 5% will be assigned a value of 2 -> test set
    status_text.text("Calculate the number of rows for each split value...")
    total_rows = len(df)
    split_0_count = int(total_rows * 0.9)
    split_1_count = int(total_rows * 0.05)
    split_2_count = total_rows - split_0_count - split_1_count
    progress_bar.progress(70)
    status_text.text("Calculate done")

    status_text.text("Create an array"
                     "with split values based on the counts...")
    split_values = np.concatenate([
        np.zeros(split_0_count),
        np.ones(split_1_count),
        np.full(split_2_count, 2)
    ])
    progress_bar.progress(80, "Processing dataset")
    status_text.text("Array created")

    status_text.text("Shuffle the array to ensure randomness...")
    np.random.shuffle(split_values)
    progress_bar.progress(85)
    status_text.text("Array shuffled")

    status_text.text("Add the 'split' column to the DataFrame...")
    df['split'] = split_values
    df['split'] = df['split'].astype(int)
    progress_bar.progress(85, "Processing dataset")
    status_text.text("'Split' column added to the DataFrame'")

    status_text.text("For this webinar,"
                     "we will just 500 rows of this dataset."
                     "Truncating...")
    df = df.head(n=500)
    progress_bar.progress(100, "Processing dataset")
    status_text.text("done")
    return df


@st.cache_data
def template_message_format_display():
    st.markdown("An user message and assistant message are automatically filled"
                " with corresponding variables and displayed "
                " in the template message format with f strings."
                " \n  - `user_message = 'Miaw'` "
                " \n  "
                " - `assistant_message = 'cat_says = Miaou \n print(cat_says)'` ")

    user_message = "Miaw"
    assistant_message = "cat_says = Miaou \n print(cat_says)"

    template_message_format = {
        "messages":
            [
                {
                    "role": "system",
                    "content": "JustAProgrammer is a programming assistant."
                    },
                {
                    "role": "user",
                    "content": f"{user_message}"
                    },
                {
                    "role": "assistant",
                    "content": f"{assistant_message}"
                    }
                ]
            }

    st.json(template_message_format, expanded=False)

    return template_message_format


def construct_user_message(instruction, input_data):
    if pd.notnull(input_data) and input_data != '':
        return f"{instruction} #### INPUT: {input_data}"
    return instruction


def populate_template(template, user_message, assistant_message):
    populated_template = template.copy()
    populated_template['messages'][1]['content'] = user_message
    populated_template['messages'][2]['content'] = assistant_message
    return populated_template


def construct_user_assistant_message(*args):
    # Concatenate multiple columns to create the user message
    return ' '.join(map(str, args))


def write_to_jsonl(dataframe, user_message_columns, assistant_message_columns, template, path):
    with open(path, 'w') as file:
        for _, row in dataframe.iterrows():
            user_message_values = [row[column] for column in user_message_columns]
            user_message = construct_user_assistant_message(*user_message_values)

            assistant_message_values = [row[column] for column in assistant_message_columns]
            assistant_message = construct_user_assistant_message(*assistant_message_values)

            populated_template = populate_template(template, user_message, assistant_message)

            file.write(json.dumps(populated_template) + '\n')


def iio_jsonl_formatting(dataframe, template_message_format, user_message_columns, assistant_message_columns):
    paths = {
        0: 'data/openai_ready/output_train.jsonl',
        1: 'data/openai_ready/output_valid.jsonl',
        2: 'data/openai_ready/output_test.jsonl'
    }

    for split, path in paths.items():
        split_df = dataframe[dataframe['split'] == split]

        write_to_jsonl(split_df, user_message_columns, assistant_message_columns, template_message_format, path)


def format_dataframe_for_display(path='data/openai_ready/output_train.jsonl'):
    # Read the JSONL file and convert it to a DataFrame
    data = []
    with open(path, 'r') as file:
        for line in file:
            data.append(json.loads(line))

    # Extract messages and format them
    roles = []
    contents = []
    indices = []
    for idx, entry in enumerate(data, 1):
        for message in entry["messages"]:
            roles.append(message["role"].upper())
            contents.append(message["content"])
            # Only add the index for the first role in each group (for the SYSTEM role)
            if message["role"] == "system":
                indices.append(idx)
            else:
                indices.append('')

    ds_df_for_display = pd.DataFrame({
        'Index': indices,
        'Role': roles,
        'Content': contents
    })

    return ds_df_for_display
