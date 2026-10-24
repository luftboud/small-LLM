import json


def load_prompts_from_json(filename: str) -> tuple(list, list):
    """
    Helper function to load the prompts from the JSON file.

    :param filename: str, path to the JSON file.
    :return: tuple(list, list), prompts and reference_answers
    """
    with open(filename) as f:
        data = json.load(f)
        prompts = [r["question"] for r in data]
        reference_answers = [r["answer"] for r in data]

        return prompts, reference_answers
