from abc import abstractmethod
from ast import List
from dataclasses import dataclass, field
import json
import re
from typing import Any, Dict

from recoma.utils.class_utils import RegistrableFromDict


@dataclass
class GeneratorParams:
    temperature: float = 0
    max_tokens: int = 100
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0
    # needed to ensure new list is created for each param
    stop: list[str] = field(default_factory=lambda: ["\n"])
    num_sequences: int = 1
    best_of: int = 1
    topk_logprobs: int = 0


@dataclass
class GenerationOutputs:
    outputs: list[str]
    scores: list[float] = field(default_factory=lambda: [])
    metadata: list[dict[str, Any]] = field(default_factory=lambda: [])


class LMGenerator(RegistrableFromDict):
    """"
    Base LM Generator class. All text-to-text generators should inherit this base registrable class
    and implement the generate method
    """
    def __init__(self, **kwargs):
        self.generator_params = GeneratorParams(**kwargs)

    @abstractmethod
    def generate(self, input_str: str) -> GenerationOutputs:
        """
        All implementations must implement this generate function that takes input text and returns
        string as output
        """
        raise NotImplementedError

    def extract_role_messages(self, input_str):
         # TODO Find a better way to handle JSON inputs
        if "\"role\": \"user\"" in input_str:
            messages_json = json.loads(input_str)
        elif "ASSISTANT:\n" in input_str:
            messages_json = []
            last_start = 0
            for m in re.finditer("(USER|ASSISTANT|SYSTEM):\n", input_str, flags=re.IGNORECASE):
                last_end = m.span()[0]
                if len(messages_json) == 0:
                    if last_end != 0:
                        raise ValueError("Start of the prompt has no assigned role: {}".format(
                            input_str[:last_end]))
                else:
                    messages_json[-1]["content"] = input_str[last_start:last_end].strip()
                mesg_type = m.group(1).lower()
                messages_json.append({"role": mesg_type, "content": None})
                last_start = m.span()[1]
            messages_json[-1]["content"] = input_str[last_start:]
        else:
            messages_json = [
                {"role": "user", "content": input_str}
            ]
        return messages_json