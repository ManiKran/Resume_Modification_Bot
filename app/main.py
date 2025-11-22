from fastapi import FastAPI
from sqlalchemy import text
from app.db.database import Base, engine
from app.routers.resume_router import router as resume_router
from app.db.database import Base, engine
from app.routers.optimize_router import router as optimize_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Resume AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "chrome-extension://mgbpoaobnhfajkaemeaalinanaecdpmi"],
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

@app.get("/reset-db")
def reset_db():
    from app.db.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return {"status": "Database reset successfully"}