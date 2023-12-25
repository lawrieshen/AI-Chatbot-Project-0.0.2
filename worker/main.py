from src.redis.config import Redis
import asyncio
from src.model.inferenceAPI import BlenderBotInferenceAPI
from src.redis.cache import Cache
from src.redis.config import Redis
from src.schema.chat import Message

redis = Redis()


async def main():
    json_client = redis.create_rejson_connection()

    await Cache(json_client).add_message_to_cache(token="18196e23-763b-4808-ae84-064348a0daff",
                                                  source="human",
                                                  message_data={
                                                      "id": "3",
                                                      "msg": "I would like to go to the moon to, would you take me?",
                                                      "timestamp": "2023-07-16 13:20:01.092109"
                                                  })

    data = await Cache(json_client).get_chat_history(token="18196e23-763b-4808-ae84-064348a0daff")
    print(data)

    message_data = data['messages'][-4:]

    input = ["" + i['msg'] for i in message_data]
    input = " ".join(input)

    res = BlenderBotInferenceAPI().query(input=input)

    msg = Message(
        msg=res
    )

    print(msg)
    await Cache(json_client).add_message_to_cache(token="18196e23-763b-4808-ae84-064348a0daff",
                                                  source="bot",
                                                  message_data=msg.model_dump())


if __name__ == "__main__":
    asyncio.run(main())
