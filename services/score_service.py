from scipy.stats import percentileofscore
import pandas as pd
import os

DATA_DIR = "data"
IMG_DIR = "static/img"
os.makedirs(IMG_DIR, exist_ok=True)

# 데이터 로드
df_flow = pd.read_csv("data/서울시 상권분석서비스(길단위인구-상권).csv", encoding="cp949")
df_pop = pd.read_csv(f"{DATA_DIR}/서울시 상권분석서비스(상주인구-상권).csv", encoding="cp949")
df_wrk = pd.read_csv(f"{DATA_DIR}/서울시 상권분석서비스(직장인구-상권).csv", encoding="cp949")
df_store = pd.read_csv(f"{DATA_DIR}/서울시 상권분석서비스(점포-상권).csv", encoding="cp949")
df_sales = pd.read_csv(f"{DATA_DIR}/서울시 상권분석서비스(추정매출-상권).csv", encoding="cp949")

def store_score(trdar_cd,induty_cd):
  latest_quarter = df_store["기준_년분기_코드"].max()
  latest_store = df_store[
      (df_store["기준_년분기_코드"] == latest_quarter) &
      (df_store["서비스_업종_코드"] == induty_cd)
  ]
  store = df_store[(df_store["상권_코드"] == trdar_cd) & (df_store["서비스_업종_코드"] == induty_cd)]
  num_stores = store["점포_수"].values[-1] if not store.empty else 0
  store_list = latest_store["점포_수"].tolist()

  # 분위수 기반 점수 (상위 몇 %인지)
  p = percentileofscore(store_list, num_stores)  # 예: 13이 상위 70%라면 p=70

  # 점수화 (많을수록 불리하니 반대로)
  score = 100 - p
  return score

def sales_score(trdar_cd, induty_cd):
    # 최신 분기
    latest_quarter = df_sales["기준_년분기_코드"].max()

    # 해당 업종 + 최신 분기 전체
    latest_sales = df_sales[
        (df_sales["기준_년분기_코드"] == latest_quarter) &
        (df_sales["서비스_업종_코드"] == induty_cd)
    ]

    # 1. 각 상권별 업종 평균 매출 (총매출 / 점포수)
    sales_group = latest_sales.groupby("상권_코드")["당월_매출_금액"].sum()
    store_group = df_store[
        (df_store["기준_년분기_코드"] == latest_quarter) &
        (df_store["서비스_업종_코드"] == induty_cd)
    ].groupby("상권_코드")["점포_수"].sum()

    avg_sales_per_store = (sales_group / store_group).dropna().tolist()

    # 2. 해당 상권의 평균 매출 계산
    current_sales = sales_group.get(trdar_cd, 0)
    current_stores = store_group.get(trdar_cd, 0)
    current_avg = current_sales / current_stores if current_stores > 0 else 0

    # 3. 분위수 점수 계산
    p = percentileofscore(avg_sales_per_store, current_avg)
    return p

def area_avg_sales_score(trdar_cd):
    # 최신 분기
    latest_quarter = df_sales["기준_년분기_코드"].max()

    # 1. 상권별 총매출 계산
    total_sales_by_area = df_sales[df_sales["기준_년분기_코드"] == latest_quarter] \
        .groupby("상권_코드")["당월_매출_금액"].sum()

    # 2. 상권별 총 매장 수 계산
    total_stores_by_area = df_store[df_store["기준_년분기_코드"] == latest_quarter] \
        .groupby("상권_코드")["점포_수"].sum()

    # 3. 평균 매출 per store = 총매출 / 매장수
    avg_sales_per_store = (total_sales_by_area / total_stores_by_area).dropna().tolist()
    print(avg_sales_per_store)

    # 4. 현재 상권의 평균 매출 계산
    current_sales = total_sales_by_area.get(trdar_cd, 0)
    current_stores = total_stores_by_area.get(trdar_cd, 0)
    current_avg = current_sales / current_stores if current_stores > 0 else 0

    # 5. 분위수 점수화
    p = percentileofscore(avg_sales_per_store, current_avg)
    return p

def floating_pop_score(trdar_cd):
    # 최신 분기
    latest_quarter = df_flow["기준_년분기_코드"].max()

    # 최신 분기 데이터만 필터링
    latest_flow = df_flow[df_flow["기준_년분기_코드"] == latest_quarter]

    # 전체 유동인구 리스트
    total_flow_list = latest_flow["총_유동인구_수"].tolist()

    # 현재 상권의 유동인구 값
    current_flow = latest_flow[latest_flow["상권_코드"] == trdar_cd]["총_유동인구_수"]
    current_val = current_flow.values[-1] if not current_flow.empty else 0

    # 분위수 점수화
    p = percentileofscore(total_flow_list, current_val)
    return p

def visitor_score(trdar_cd, induty_cd):
    # 최신 분기
    latest_quarter = df_sales["기준_년분기_코드"].max()

    # 최신 분기 + 업종 필터
    latest_sales = df_sales[
        (df_sales["기준_년분기_코드"] == latest_quarter) &
        (df_sales["서비스_업종_코드"] == induty_cd)
    ]

    # 1. 전체 상권들의 일 방문자 수 리스트 (= 결제건수 / 30)
    latest_sales["일방문자수"] = latest_sales["당월_매출_건수"]
    visitor_list = latest_sales["일방문자수"].tolist()

    # 2. 현재 상권의 일 방문자 수
    current = latest_sales[latest_sales["상권_코드"] == trdar_cd]
    current_visitor = (current["당월_매출_건수"].values[-1]) if not current.empty else 0

    # 3. 분위수 점수화
    p = percentileofscore(visitor_list, current_visitor)
    return p

def score_summary(trdar_cd, induty_cd):
    # 각 항목별 점수 계산
    score_floating = floating_pop_score(trdar_cd)                    # 유동인구
    score_store = store_score(trdar_cd, induty_cd)                   # 동종업종 점포 수
    score_sales = sales_score(trdar_cd, induty_cd)                   # 동종업종 평균 매출
    score_area = area_avg_sales_score(trdar_cd)                      # 상권 평균 매출
    score_visitor = visitor_score(trdar_cd, induty_cd)              # 일방문자 수

    # 가중치
    weight = {
        "유동인구": 0.25,
        "동종업종_점포수": 0.20,
        "동종업종_평균매출": 0.20,
        "상권_평균매출": 0.20,
        "일방문자수": 0.15
    }

    # 최종 가중 합산 점수
    final_score = (
        score_floating * weight["유동인구"] +
        score_store * weight["동종업종_점포수"] +
        score_sales * weight["동종업종_평균매출"] +
        score_area * weight["상권_평균매출"] +
        score_visitor * weight["일방문자수"]
    )

    return {
        "유동인구": round(score_floating, 1),
        "동종업종_점포수": round(score_store, 1),
        "동종업종_평균매출": round(score_sales, 1),
        "상권_평균매출": round(score_area, 1),
        "일방문자수": round(score_visitor, 1),
        "최종점수": round(final_score, 1)
    }



