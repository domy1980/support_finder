from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import llm, diseases, search, nando
from app.database import engine
from app.models import disease, organization

# データベーステーブルの作成
disease.Base.metadata.create_all(bind=engine)
try:
    organization.Base.metadata.create_all(bind=engine)
except:
    pass  # organizationモデルがまだない場合はスキップ

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
app.include_router(diseases.router, prefix=f"{settings.API_V1_STR}/diseases", tags=["diseases"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
app.include_router(nando.router, prefix=f"{settings.API_V1_STR}/nando", tags=["nando"])

@app.get("/")
async def root():
    return {"message": "Disease Support Finder API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
