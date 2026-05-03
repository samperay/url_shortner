"""Main application."""


from fastapi import FastAPI

from app.database import Base, engine
from app.routers import url_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener",
    description="Simple URL Shortener using FastAPI and SQLite",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(url_router.router)
