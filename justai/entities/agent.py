from typing import Dict, Optional
import copy


class Agent:
    """
    Represents an agent with a name, system prompt, and dataset generation prompts.

    Attributes:
    - name (str): The name of the agent.
    - system_prompt (str): The system prompt associated with the agent.
    - dataset_generation_prompts (Optional[Dict[str, str]]): A dictionary containing dataset generation
      prompts. The keys are labels and the values are specific prompt details.
      Defaults to an empty dictionary.

    Methods:
    - to_dict: Returns a dictionary representation of the agent.
    """
    def __init__(
        self,
        name: str,
        system_prompt: str,
        dataset_generation_prompts: Optional[Dict[str, str]] = None
    ):
        self.name = name
        self.system_prompt = system_prompt
        if dataset_generation_prompts is None:
            self.dataset_generation_prompts = {}
        else:
            self.dataset_generation_prompts = copy.deepcopy(dataset_generation_prompts)

    def to_dict(self):
        return {
            'name': self.name,
            'system_prompt': self.system_prompt,
            'dataset_generation_prompts': self.dataset_generation_prompts
        }
