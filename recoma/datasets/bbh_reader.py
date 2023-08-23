import json

from recoma.datasets.reader import DatasetReader, Example


@DatasetReader.register("bbh")
class BBHReader(DatasetReader):
    """
    Note that this is a reader for the BBH-formatted data with the format:
        ```
            "examples": [
                {
                "input": "..."
                "target": "..."
                }
            ...
            ]
        ```
    """

    def read_examples(self, file: str):
        with open(file, 'r') as input_fp:
            input_json = json.load(input_fp)
        qid = 0
        for example in input_json["examples"]:
            question = example["input"]
            qid += 1
            answer = example["target"]
            yield Example(qid=str(qid), question=question, gold_answer=answer, paras=[])
