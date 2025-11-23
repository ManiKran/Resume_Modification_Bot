from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.database import Base, engine
from app.routers.resume_router import router as resume_router
from app.routers.optimize_router import router as optimize_router

app = FastAPI(title="Resume AI Backend")

# ----------------------------------------------------------
# 🚀 1. REQUIRED ON RAILWAY: Fix HTTPS → HTTP redirect issues
# ----------------------------------------------------------
# Ensures FastAPI trusts X-Forwarded-For / X-Forwarded-Proto headers
app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts="*"
)

# ----------------------------------------------------------
# 🚀 2. CORS SETTINGS (EXTENSION + RAILWAY http/https)
# ----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://mgbpoaobnhfajkaemeaalinanaecdpmi",
        "https://resumemodificationbot-production.up.railway.app",
        "http://resumemodificationbot-production.up.railway.app",   # HTTP fallback
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------
# 🚀 3. Database startup
# ----------------------------------------------------------
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# ----------------------------------------------------------
# 🚀 4. Routers
# ----------------------------------------------------------
app.include_router(resume_router)
app.include_router(optimize_router)

# ----------------------------------------------------------
# 🚀 5. Root endpoint
# ----------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Resume AI Backend is running!"}

# ----------------------------------------------------------
# 🚀 6. Serve generated DOCX files
# ----------------------------------------------------------
app.mount("/generated", StaticFiles(directory="generated"), name="generated")