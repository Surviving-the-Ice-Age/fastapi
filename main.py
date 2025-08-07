from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import analysis, sentiment

app = FastAPI(title="서울시 상권 분석 API")

# 정적 이미지 (그래프)
app.mount("/static", StaticFiles(directory="static/img"), name="static")

# 분석 API 등록
app.include_router(analysis.router, prefix="/api", tags=["분석 API"])
app.include_router(sentiment.router, prefix="/sentiment", tags=["감성 분석 API"])
