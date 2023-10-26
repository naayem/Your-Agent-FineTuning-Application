import streamlit as st


def display_code_generation_dataset():
    generation_dataset_code = """
    from google.colab import data_table;
    data_table.enable_dataframe_formatter()
    import numpy as np; np.random.seed(123)
    import pandas as pd

    df = pd.read_json("https://raw.githubusercontent.com/"
                "sahil280114/codealpaca/master/data/code_alpaca_20k.json")

    # We're going to create a new column called `split` where:
    # 90% will be assigned a value of 0 -> train set
    # 5% will be assigned a value of 1 -> validation set
    # 5% will be assigned a value of 2 -> test set
    # Calculate the number of rows for each split value
    total_rows = len(df)
    split_0_count = int(total_rows * 0.9)
    split_1_count = int(total_rows * 0.05)
    split_2_count = total_rows - split_0_count - split_1_count

    # Create an array with split values based on the counts
    split_values = np.concatenate([
        np.zeros(split_0_count),
        np.ones(split_1_count),
        np.full(split_2_count, 2)
    ])

    # Shuffle the array to ensure randomness
    np.random.shuffle(split_values)

    # Add the 'split' column to the DataFrame
    df['split'] = split_values
    df['split'] = df['split'].astype(int)

    # For this webinar, we will just 500 rows of this dataset.
    df = df.head(n=500)
    """

    with st.expander('Show code'):
        st.code(generation_dataset_code, language='python')
    return


def cell_observations_from_zero_shot_prompting_results():
    st.markdown(r'''
    1. The base Llama-2 model is generally good
    at producing coherent English text as responses.
    2. When it doesn't know how to respond
    (which seems to be true most of the times
    we want it to follow an instruction),
    it just returns the input over and over again
    until the token limit is reached.
    Sometimes it even modifies the original instruction in the process.
    3. It doesn't know when to stop producing a response,
    i.e., it gets confused and just produces till we set a hard stop
    through the number of maximum allowed tokens.
    In an ideal scenario, the probability distribution
    being used to generate the next token predicts
    a stop token at the right point in time.
    4. It doesn't get even one of the input prompts correct.

    ⭐ **None of these results are surprising,
    but it goes to show that while a model like Llama-2
    can be good on general tasks,
    it can often be very poor at performing domain specific
    tasks out of the box just through zero shot/regular prompting
    (pretrained knowledge without any additional context)** ⭐
    ''')


def cell_prompt_templating_and_zero_shot_inference():
    st.markdown(r'''

    **Zero-shot learning is a capability enabled by Large Language Models,
    allowing them to generalize to tasks or domains
    they have never been explicitly trained on.**
    This approach leverages the inherent knowledge
    and linguistic understanding encoded within the
    model during its pre-training phase.

    Zero-shot learning involves presenting
    the model with a task description or prompt,
    along with some context, and expecting it to generate a relevant
    response or output.
    The key idea is that the model can understand and generate coherent
    content even for tasks it hasn't been explicitly fine-tuned for.
    ''')

    st.image("https://ludwig.ai/latest/images/icl_zero_shot_learning.png")

    st.markdown(r'''
    In Ludwig, there are two parameters we can use to control
    prompting and the quality of generation when trying to use
    the LLM for zero-shot inference:
    - `prompt`: the prompt parameter can be used to
    - Provide necessary boilerplate needed to make the LLM
    respond in the correct way (for example, with a response
    to a question rather than a continuation of the input sequence).
    - Combine multiple columns from a dataset into a single
    text input feature.
    - Provide additional context to the model that can help
    it understand the task, or provide restrictions to prevent
    hallucinations (producing false information confidently). <br>

    All of this can be configured through the nested keyword called
    `template`. The template allows regular text to describe the task,
    but also allows two special group of keywords that can be used:
    - **Reserved Keywords**: `{__sample__}`, `{__task__}` and `{__context__}`
    - **Feature Names**: If you have additional
    feature names you want to combine
    into your prompt, you can add them using the same `{}`
    template without the `__`.
     For e.g., in our case, we have three columns: `instruction`,
     `input` and `output`. We can refer to the `instruction`
     and `input` data via the `{instruction}` and `{input}`.
     We will see this in our example below.

    See the full docs for prompt
    [here](https://ludwig.ai/latest/configuration/large_language_model/#prompt).

    - `generation`: You may often want to control the generation process,
    such as what token decoding strategy to use,
    how many new tokens to produce,
    which tokens to exclude, or how diverse you want the generated text to be.
    See the full docs
    [here](https://ludwig.ai/latest/configuration/large_language_model/#generation).

    Let's try and perform some zero-shot prompting
    with Ludwig to see how the model does on our task out of the box.
    ''')


def display_prompt_templating_zero_shot_code():
    prompt_templating_zero_shot_code = r'''
        zero_shot_config = yaml.safe_load(
        """
        model_type: llm
        base_model: meta-llama/Llama-2-7b-hf

        input_features:
            - name: instruction
            type: text

        output_features:
            - name: output
            type: text

        prompt:
            template: >-
            Below is an instruction that describes a task, paired with an input
            that may provide further context.
            Write a response that appropriately
            completes the request.

            ### Instruction: {instruction}

            ### Input: {input}

            ### Response:

        generation:
            temperature: 0.1
            # Temperature is used to control the randomness of predictions.
            max_new_tokens: 512

        preprocessing:
            split:
            type: fixed

        quantization:
            bits: 4
        """
        )

        model = LudwigModel(config=zero_shot_config,
        logging_level=logging.INFO)
        results = model.train(dataset=df)
    '''
    st.code(prompt_templating_zero_shot_code, language='python')
    return
