from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import llm

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの登録
app.include_router(llm.router, prefix=f"{settings.API_V1_STR}/llm", tags=["llm"])

@app.get("/")
async def root():
    return {"message": "Disease Support Finder API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
