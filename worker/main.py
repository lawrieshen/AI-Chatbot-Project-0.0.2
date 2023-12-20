from src.redis.config import Redis
import asyncio
from src.model.inferenceAPI import BlenderBotInferenceAPI
from src.redis.cache import Cache
from src.schema.chat import Message

redis = Redis()


async def main():
    json_client = redis.create_rejson_connection()
    redis_client = await redis.create_connection()

    await Cache(json_client).add_message_to_cache(token="f000c5a9-7ec9-4e66-8780-bc9d5b12fd25", source="human",
                                                  message_data={
                                                      "id": "3",
                                                      "msg": "How to survive as a Software Engineering student with "
                                                             "AI prevailing?",
                                                      "timestamp": "2022-07-16 13:20:01.092109"
                                                  })

    data = await Cache(json_client).get_chat_history(token="f000c5a9-7ec9-4e66-8780-bc9d5b12fd25")
    print(data)

    message_data = data['messages'][-4:]

    input = ["" + i['msg'] for i in message_data]
    input = " ".join(input)

    res = BlenderBotInferenceAPI().query(input=input)

    msg = Message(
        msg=res
    )

    print(msg)
    await Cache(json_client).add_message_to_cache(token="f000c5a9-7ec9-4e66-8780-bc9d5b12fd25", source='bot',
                                                  message_data=msg.model_dump())


if __name__ == "__main__":
    asyncio.run(main())
