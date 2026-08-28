from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes.chat import router as chat_router


app = FastAPI(
    title="Northstar AI Sales Agent",
    version="1.0.0"
)


app.include_router(
    chat_router,
    prefix="/api"
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def root():

    return FileResponse("frontend/index.html")


@app.get("/health")
def health():

    return {
        "message": "Northstar AI Sales Agent is running"
    }
