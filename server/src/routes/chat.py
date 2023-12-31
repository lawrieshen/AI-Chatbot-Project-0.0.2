import asyncio
import os
import sys
import time
import uuid
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException
from ..socket.connection import ConnectionManager
from ..socket.utils import get_token
from ..redis.producer import Producer
from ..redis.config import Redis
from ..schema.chat import Chat
from rejson import Path
from ..redis.stream import StreamConsumer
from ..redis.cache import Cache
from threading import Timer

chat = APIRouter()
manager = ConnectionManager()
redis = Redis()


# @route   POST /token
# @desc    Route to generate chat token
# @access  Public


@chat.post("/token")
async def token_generator(name: str, request: Request):
    token = str(uuid.uuid4())

    if name == "":
        raise HTTPException(status_code=400, detail={
            "loc": "name", "msg": "Enter a valid name"})

    # Create a new chat session
    json_client = redis.creat_rejson_connection()

    chat_session = Chat(
        token=token,
        messages=[],
        name=name
    )

    # Store chat session in redis JSON with the token as key
    json_client.jsonset(str(token), Path.rootPath(), chat_session.dict())

    # Set a timeout for redis data
    redis_client = await redis.create_connection()
    await redis_client.expire(str(token), 3600)

    return chat_session.dict()


# @route   POST /refresh_token
# @desc    Route to refresh token
# @access  Public


@chat.post("/refresh_token")
async def refresh_token(request: Request, token: str):
    json_client = redis.create_rejson_connection()
    cache = Cache(json_client)
    data = await cache.get_chat_history(token)

    if data is None:
        raise HTTPException(
            status_code=400, detail="Session expired or does not exist"
        )
    else:
        return data


# @route   Websocket /chat
# @desc    Socket for chatbot
# @access  Public

@chat.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(get_token), validity=None):
    await manager.connect(websocket)
    redis_client = await redis.create_connection()
    producer = Producer(redis_client)
    json_client = redis.creat_rejson_connection()
    consumer = StreamConsumer(redis_client)
    try:
        while True:
            data = await websocket.receive_text()
            stream_data = {token: data}
            await producer.add_to_stream(stream_data, "message_channel")
            # worker.py detected new messages then put the response back to the response_channel
            await asyncio.sleep(0.5)
            response = await consumer.consume_stream(stream_channel="response_channel", block=0)

            for stream, messages in response:
                for message in messages:
                    response_token = [k.decode('utf-8')
                                      for k, v in message[1].items()][0]

                    if token == response_token:
                        response_message = [v.decode('utf-8')
                                            for k, v in message[1].items()][0]

                        await manager.send_personal_message(response_message, websocket)

                    await consumer.delete_message(stream_channel="response_channel",
                                                  message_id=message[0].decode('utf-8'))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
