class AgentDTO:
    def __init__(self, name, system_prompt, _id=None):
        self._id = _id
        self.name = name
        self.system_prompt = system_prompt
