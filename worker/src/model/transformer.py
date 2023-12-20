import os
from dotenv import load_dotenv
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration

load_dotenv()


class BlenderBotTransformer:
    def __init__(self):
        self.mname = os.environ.get('MODEL_NAME')
        print(self.mname)
        self.model = BlenderbotForConditionalGeneration.from_pretrained(self.mname)
        self.payload = {
            "inputs": "",
            "parameters": {
                "return_full_text": False,
                "use_cache": True,
                "max_new_tokens": 25
            }
        }

    def query(self, input: str) -> list:
        tokenizer = BlenderbotTokenizer.from_pretrained(self.mname)
        UTTERANCE = input
        inputs = tokenizer([UTTERANCE], return_tensors="pt")
        reply_ids = self.model.generate(**inputs)
        print(tokenizer.batch_decode(reply_ids))
        return tokenizer.batch_decode(reply_ids)


if __name__ == "__main__":
    BlenderBotTransformer().query("My friends are cool but they eat too many carbs.")
