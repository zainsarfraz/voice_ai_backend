from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api import v1_router

app = FastAPI(
    title="Voice AI backend",
    version="0.1.0",
    description="A scalable voice AI Backend server",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=status.HTTP_200_OK, tags=["Root"])
def read_root():
    return {"message": "Welcome to the Voice AI Backend"}


app.include_router(v1_router.routes, prefix="/api")
