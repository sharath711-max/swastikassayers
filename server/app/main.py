from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import init_db

# Import routers
from .routers import customers, credit_history, gold_certificate, gold_test, photo_certificate, silver_certificate, weight_loss, globals

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_db()
    yield
    # Cleanup on shutdown if needed
    pass

app = FastAPI(
    title="Swastik Assayers API",
    description="Backend API for Swastik Assayers - Gold and Silver Certification Business",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(customers.router, prefix="/api/v1", tags=["customers"])
app.include_router(credit_history.router, prefix="/api/v1", tags=["credit-history"])
app.include_router(gold_certificate.router, prefix="/api/v1", tags=["gold-certificate"])
app.include_router(gold_test.router, prefix="/api/v1", tags=["gold-test"])
app.include_router(photo_certificate.router, prefix="/api/v1", tags=["photo-certificate"])
app.include_router(silver_certificate.router, prefix="/api/v1", tags=["silver-certificate"])
app.include_router(weight_loss.router, prefix="/api/v1", tags=["weight-loss"])
app.include_router(globals.router, prefix="/api/v1", tags=["globals"])

@app.get("/")
async def root():
    return {"status": "ok", "message": "Swastik Assayers API server running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)