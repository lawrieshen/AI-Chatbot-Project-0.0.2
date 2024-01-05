from contextlib import asynccontextmanager

import fastapi
from fastapi import FastAPI, Request
import uvicorn
import os
from dotenv import load_dotenv
from src.routes.chat import chat
import signal
from fastapi.responses import JSONResponse

load_dotenv()


@asynccontextmanager
async def lifespan(api:FastAPI):
    yield
    print('Server shutting down...')


api = FastAPI(lifespan=lifespan)
api.include_router(chat)


@api.get("/test")
async def root():
    return {"msg": "API is Online"}


@api.get("/shutdown")
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return fastapi.Response(status_code=200, content='Server shutting down...')


if __name__ == "__main__":
    uvicorn.run("main:api", host="0.0.0.0", port=3500, workers=4, reload=True)
