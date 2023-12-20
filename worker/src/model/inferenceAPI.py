import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()


class BlenderBotInferenceAPI:
    def __init__(self):
        self.url = os.environ.get('MODEL_URL')
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('HUGGINGFACE_INFERENCE_TOKEN')}"}
        self.payload = {
            "inputs": "",
            "parameters": {
                "use_cache": True,
            }

        }

    def query(self, input: str) -> list:
        self.payload["inputs"] = input
        data = json.dumps(self.payload)
        response = requests.request(
            "POST", self.url, headers=self.headers, data=data)
        data = json.loads(response.content.decode("utf-8"))
        print(data)
        text = data['generated_text']
        res = str(text.split("Human:")[0]).strip("\n").strip()
        return res


if __name__ == "__main__":
    BlenderBotInferenceAPI().query("Will artificial intelligence replaces software engineer jobs?")
