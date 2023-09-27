import numpy as np
import pandas as pd
import streamlit as st
from ludwig.api import LudwigModel
import logging
import yaml

import locale; locale.getpreferredencoding = lambda: "UTF-8"


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


zero_shot_config = yaml.safe_load(
  """
  model_type: llm
  base_model: huggyllama/llama-7b

  input_features:
    - name: instruction
      type: text

  output_features:
    - name: output
      type: text

  prompt:
    template: >-
      Below is an instruction that describes a task, paired with an input
      that may provide further context. Write a response that appropriately
      completes the request.

      ### Instruction: {instruction}

      ### Input: {input}

      ### Response:

  generation:
    temperature: 0.1 # Temperature is used to control the randomness of predictions.
    max_new_tokens: 512

  preprocessing:
    split:
      type: fixed

  quantization:
    bits: 4
  """
)


def zero_shot_run(df):

    model = LudwigModel(config=zero_shot_config, logging_level=logging.INFO)
    results = model.train(dataset=df)
    st.write(results)
    return results
