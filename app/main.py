from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.database import Base, engine
from app.routers.resume_router import router as resume_router
from app.routers.optimize_router import router as optimize_router

app = FastAPI(title="Resume AI Backend")

# 🚀 Fix HTTPS redirect issues behind Railway
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 🚀 CORS for Chrome Extension + Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://jlkkglkngkggobainneppchmdkfeklod"   # your REAL extension ID
    ],
    allow_origin_regex=r"https://.*\.railway\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(resume_router)
app.include_router(optimize_router)

@app.get("/")
def root():
    return {"message": "Resume AI Backend is running!"}

app.mount("/generated", StaticFiles(directory="generated"), name="generated")