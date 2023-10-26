import streamlit as st

import json
import tiktoken
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt


def data_loading_openft(data_path="data/toy_chat_fine_tuning.jsonl"):

    # Load the dataset
    with open(data_path, 'r', encoding='utf-8') as f:
        dataset = [json.loads(line) for line in f]

    return dataset


def validate_format(dataset):
    # Format error checks
    format_errors = defaultdict(int)

    for ex in dataset:
        if not isinstance(ex, dict):
            format_errors["data_type"] += 1
            continue

        messages = ex.get("messages", None)
        if not messages:
            format_errors["missing_messages_list"] += 1
            continue

        for message in messages:
            if "role" not in message or "content" not in message:
                format_errors["message_missing_key"] += 1

            if any(k not in ("role", "content", "name") for k in message):
                format_errors["message_unrecognized_key"] += 1

            if message.get("role", None) not in ("system", "user", "assistant"):
                format_errors["unrecognized_role"] += 1

            content = message.get("content", None)
            if not content or not isinstance(content, str):
                format_errors["missing_content"] += 1

        if not any(message.get("role", None) == "assistant" for message in messages):
            format_errors["example_missing_assistant_message"] += 1

    if format_errors:
        st.warning("Found errors:")
        for k, v in format_errors.items():
            st.write(f"{k}: {v}")
    else:
        st.success("No errors found")
    return format_errors


# not exact!
# simplified from https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
encoding = tiktoken.get_encoding("cl100k_base")


def num_tokens_from_messages(messages, tokens_per_message=3, tokens_per_name=1):
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens


def num_assistant_tokens_from_messages(messages):
    num_tokens = 0
    for message in messages:
        if message["role"] == "assistant":
            num_tokens += len(encoding.encode(message["content"]))
    return num_tokens


def print_distribution(values, name):
    with st.expander(f"\n `{name}` Distribution:"):
        dist1, dist2, dist3 = st.columns(3)
        dist1.metric("min / max:", f"{min(values)} / {max(values)}")
        dist2.metric("mean / median:", f"{np.mean(values):.2f} / {np.median(values):.2f}")
        dist3.metric("p5 / p95:", f"{np.quantile(values, 0.1):.2f} / {np.quantile(values, 0.9):.2f}")

        plt.figure(figsize=(8, 1))
        plt.boxplot(values, vert=False)
        plt.title("Boxplot of num_total_tokens_per_example")
        plt.xticks(rotation=45)
        plt.xlabel("Number of Tokens")

        st.pyplot(plt)


def count_tokens_and_data_warnings(dataset):
    # Warnings and tokens counts
    n_missing_system = 0
    n_missing_user = 0
    n_messages = []
    convo_lens = []
    assistant_message_lens = []

    for ex in dataset:
        messages = ex["messages"]
        if not any(message["role"] == "system" for message in messages):
            n_missing_system += 1
        if not any(message["role"] == "user" for message in messages):
            n_missing_user += 1
        n_messages.append(len(messages))
        convo_lens.append(num_tokens_from_messages(messages))
        assistant_message_lens.append(num_assistant_tokens_from_messages(messages))

    size_cols = st.columns(3)
    st.write("First example from the dataset:")
    for i, message in enumerate(dataset[0]["messages"]):
        size_cols[i].write(f"{i+1}- {message['role']}:")
        size_cols[i].json(message, expanded=False)
    size_cols[0].metric("Num examples:", len(dataset))
    size_cols[1].metric("Num examples missing system message:", n_missing_system)
    size_cols[2].metric("Num examples missing user message:", n_missing_user)
    print_distribution(n_messages, "num_messages_per_example")
    print_distribution(convo_lens, "num_total_tokens_per_example")
    print_distribution(assistant_message_lens, "num_assistant_tokens_per_example")
    n_too_long = sum(convo_len > 4096 for convo_len in convo_lens)
    if n_too_long == 0:
        st.success("No examples are over the 4096 token limit")
    else:
        st.warning(f"\n{n_too_long} examples may be over the 4096 token limit, they'll be truncated during fine-tuning")
    return convo_lens


def estimate_cost(dataset, convo_lens, n_epochs_manual, cost_per_1k_tokens):
    # Pricing and default n_epochs estimate
    MAX_TOKENS_PER_EXAMPLE = 4096

    TARGET_EPOCHS = 3
    MIN_TARGET_EXAMPLES = 100
    MAX_TARGET_EXAMPLES = 25000
    MIN_DEFAULT_EPOCHS = 1
    MAX_DEFAULT_EPOCHS = 25

    n_epochs_default = TARGET_EPOCHS
    n_train_examples = len(dataset)
    if n_train_examples * TARGET_EPOCHS < MIN_TARGET_EXAMPLES:
        n_epochs_default = min(MAX_DEFAULT_EPOCHS, MIN_TARGET_EXAMPLES // n_train_examples)
    elif n_train_examples * TARGET_EPOCHS > MAX_TARGET_EXAMPLES:
        n_epochs_default = max(MIN_DEFAULT_EPOCHS, MAX_TARGET_EXAMPLES // n_train_examples)

    n_billing_tokens_in_dataset = sum(min(MAX_TOKENS_PER_EXAMPLE, length) for length in convo_lens)

    col1, col2 = st.columns(2)
    col1.write(
        f"1️⃣ Dataset has `~{n_billing_tokens_in_dataset}`\
            tokens that will be charged for during training `(1 epoch)`\n\n"
        f"2️⃣ \n - By default, you'll train for `{n_epochs_default}` epochs on this dataset\n\n\
            - Or manually chosen `{n_epochs_manual}` epochs\n\n"
        f"3️⃣ \n By default, you'll be charged for `~{n_epochs_default * n_billing_tokens_in_dataset}`\
            tokens\n\n - Or manually chosen `~{n_epochs_manual * n_billing_tokens_in_dataset}` tokens"
        )

    col2.write(
        f"4️⃣ The cost of training per 1k tokens is ```$ {cost_per_1k_tokens:.4f}```\n\n"
        f"5️⃣ \n - so the total cost for `{n_epochs_default}epochs` by default is\
            `~${n_epochs_default * n_billing_tokens_in_dataset * cost_per_1k_tokens /1000:.2f}`\n\n -\
                or manually chosen `{n_epochs_manual} epochs`\
                    `~${n_epochs_manual * n_billing_tokens_in_dataset * cost_per_1k_tokens /1000:.2f}`"
        )
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Total default cost",
                f"{n_epochs_default * n_billing_tokens_in_dataset * cost_per_1k_tokens / 1000 :.2f} $")
    col2.metric("Total manual cost",
                f"{n_epochs_manual * n_billing_tokens_in_dataset * cost_per_1k_tokens / 1000 :.2f} $")
