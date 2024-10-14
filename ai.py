from langflow.load import run_flow_from_json
from dotenv import load_dotenv
import requests
from typing import Optional
import json
import os

load_dotenv()

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "34c16f5c-70e4-4bb6-9c51-89a41a653efd"
APPLICATION_TOKEN = os.getenv("LANGFLOW_TOKEN")


def dict_to_string(obj, level=0):
    strings = []
    indent = "  " * level  # Indentation for nested levels
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                nested_string = dict_to_string(value, level + 1)
                strings.append(f"{indent}{key}: {nested_string}")
            else:
                strings.append(f"{indent}{key}: {value}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            nested_string = dict_to_string(item, level + 1)
            strings.append(f"{indent}Item {idx + 1}: {nested_string}")
    else:
        strings.append(f"{indent}{obj}")

    return ", ".join(strings)


def ask_ai(profile, question):
    TWEAKS = {
        "TextInput-XjIKI": {
            "input_value": question
        },
        "TextInput-176Ns": {
            "input_value": dict_to_string(profile)
        },
    }

    result = run_flow_from_json(flow="AskAIV2.json",
                                input_value="message",
                                fallback_to_env_vars=True,
                                tweaks=TWEAKS)

    return result[0].outputs[0].results["text"].data["text"]


def get_macros(profile, goals):
    TWEAKS = {
        "TextInput-PR5Jb": {
            "input_value": ", ".join(goals)
        },
        "TextInput-PrfY9": {
            "input_value": dict_to_string(profile)
        }
    }
    return run_flow("", tweaks=TWEAKS, application_token=APPLICATION_TOKEN)


def run_flow(message: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  application_token: Optional[str] = None) -> dict:
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/macros"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    
    return json.loads(response.json()["outputs"][0]["outputs"][0]["results"]["text"]["data"]["text"])
