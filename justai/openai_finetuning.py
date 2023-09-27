import openai

# Create a fine-tuning job with an already uploaded file
openai.FineTuningJob.create(training_file="file-abc123", model="gpt-3.5-turbo")

# List 10 fine-tuning jobs
openai.FineTuningJob.list(limit=10)

# Retrieve the state of a fine-tune
openai.FineTuningJob.retrieve("ft-abc123")

# Cancel a job
openai.FineTuningJob.cancel("ft-abc123")

# List up to 10 events from a fine-tuning job
openai.FineTuningJob.list_events(id="ft-abc123", limit=10)

# Delete a fine-tuned model (must be an owner of the org the model was created in)
openai.Model.delete("ft:gpt-3.5-turbo:acemeco:suffix:abc123")


# To log the training results from fine-tuning to Weights & Biases use:
# openai wandb sync
