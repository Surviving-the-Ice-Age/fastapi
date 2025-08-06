import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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


def make_img_path(name):
    return os.path.join(IMG_DIR, f"{name}.png")

# 1. 상주인구 성별/연령대 비율
def plot_resident_gender_age_ratio(trdar_cd):
    df = df_pop[df_pop["상권_코드"] == trdar_cd].sort_values("기준_년분기_코드")
    if df.empty:
        return {"error": "해당 상권 데이터가 없습니다."}
    
    pop = df.iloc[-1]
    total = pop["총_상주인구_수"]

    age_groups = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
    male_cols = ["남성연령대_10_상주인구_수", "남성연령대_20_상주인구_수", "남성연령대_30_상주인구_수",
                 "남성연령대_40_상주인구_수", "남성연령대_50_상주인구_수", "남성연령대_60_이상_상주인구_수"]
    female_cols = ["여성연령대_10_상주인구_수", "여성연령대_20_상주인구_수", "여성연령대_30_상주인구_수",
                   "여성연령대_40_상주인구_수", "여성연령대_50_상주인구_수", "여성연령대_60_이상_상주인구_수"]

    male_pct = [pop[col] / total * 100 for col in male_cols]
    female_pct = [pop[col] / total * 100 for col in female_cols]

    x = np.arange(len(age_groups))
    width = 0.35

    plt.figure(figsize=(10, 5))
    bars1 = plt.bar(x - width/2, male_pct, width, label='남성', color='skyblue')
    bars2 = plt.bar(x + width/2, female_pct, width, label='여성', color='mediumturquoise')

    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.3, f"{height:.1f}%", ha='center', fontsize=9)

    for bar in bars2:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.3, f"{height:.1f}%", ha='center', fontsize=9)

    plt.ylabel("단위: %")
    plt.title("성별, 연령별 주거인구 현황")
    plt.xticks(x, age_groups)
    plt.ylim(0, max(max(male_pct), max(female_pct)) + 5)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 이미지 저장
    fname = f"resident_gender_age_{trdar_cd}"
    save_path = make_img_path(fname)
    plt.savefig(save_path)
    plt.close()

    # 인사이트 생성
    combined = []
    labels = []
    for i in range(len(age_groups)):
        combined.append(male_pct[i])
        labels.append(f"남성, {age_groups[i]}")
        combined.append(female_pct[i])
        labels.append(f"여성, {age_groups[i]}")

    top_idx = np.argmax(combined)
    insight = f"{labels[top_idx]}({combined[top_idx]:.1f}%) 주거인구가 가장 많아요."

    return {
        "상권코드": trdar_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 2. 유동인구 시간대 비율
def plot_floating_time_ratio(trdar_cd):
    df = df_flow[df_flow["상권_코드"] == trdar_cd].sort_values("기준_년분기_코드")
    if df.empty:
        return {"error": "해당 상권 데이터가 없습니다."}

    flow = df.iloc[-1]
    total = flow["총_유동인구_수"]

    time_labels = ["00~06시", "06~11시", "11~14시", "14~17시", "17~21시", "21~24시"]
    time_cols = ["시간대_00_06_유동인구_수", "시간대_06_11_유동인구_수", "시간대_11_14_유동인구_수",
                 "시간대_14_17_유동인구_수", "시간대_17_21_유동인구_수", "시간대_21_24_유동인구_수"]

    time_pct = [flow[col] / total * 100 for col in time_cols]

    # 최고 시간대 탐색
    top_idx = np.argmax(time_pct)
    insight = f"{time_labels[top_idx]} 유동인구가 가장 많습니다. ({time_pct[top_idx]:.1f}%)"

    # 그래프
    plt.figure(figsize=(10, 5))
    plt.plot(time_labels, time_pct, marker="o", linewidth=3, color="deepskyblue")
    for i, v in enumerate(time_pct):
        plt.text(i, v + 0.8, f"{v:.1f}%", ha='center', fontsize=9)

    plt.ylim(0, max(time_pct) + 5)
    plt.title("시간대별 유동인구 현황")
    plt.ylabel("단위: 시간대별 유동인구 비율(%)")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 저장
    fname = f"floating_time_{trdar_cd}"
    save_path = make_img_path(fname)
    plt.savefig(save_path)
    plt.close()

    return {
        "상권코드": trdar_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 3. 직장인구 성별/연령대
def plot_workplace_gender_age_ratio(trdar_cd):
    df = df_wrk[df_wrk["상권_코드"] == trdar_cd].sort_values("기준_년분기_코드")
    if df.empty:
        return {"error": "해당 상권 데이터가 없습니다."}

    wrk = df.iloc[-1]
    total = wrk["총_직장_인구_수"]

    age_groups = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
    male_cols = ["남성연령대_10_직장_인구_수", "남성연령대_20_직장_인구_수", "남성연령대_30_직장_인구_수",
                 "남성연령대_40_직장_인구_수", "남성연령대_50_직장_인구_수", "남성연령대_60_이상_직장_인구_수"]
    female_cols = ["여성연령대_10_직장_인구_수", "여성연령대_20_직장_인구_수", "여성연령대_30_직장_인구_수",
                   "여성연령대_40_직장_인구_수", "여성연령대_50_직장_인구_수", "여성연령대_60_이상_직장_인구_수"]

    male_pct = [wrk[col] / total * 100 for col in male_cols]
    female_pct = [wrk[col] / total * 100 for col in female_cols]

    x = np.arange(len(age_groups))
    width = 0.35

    plt.figure(figsize=(10, 5))
    bars1 = plt.bar(x - width/2, male_pct, width, label='남성', color='cornflowerblue')
    bars2 = plt.bar(x + width/2, female_pct, width, label='여성', color='lightseagreen')

    for bar in bars1 + bars2:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.3, f"{height:.1f}%", ha='center', fontsize=9)

    plt.ylabel("단위: %")
    plt.title("성별, 연령별 직장인구 현황")
    plt.xticks(x, age_groups)
    plt.ylim(0, max(max(male_pct), max(female_pct)) + 5)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 이미지 저장
    fname = f"workplace_gender_age_{trdar_cd}"
    save_path = make_img_path(fname)
    plt.savefig(save_path)
    plt.close()

    # 인사이트 출력
    combined = []
    labels = []
    for i in range(len(age_groups)):
        combined.append(male_pct[i])
        labels.append(f"남성, {age_groups[i]}")
        combined.append(female_pct[i])
        labels.append(f"여성, {age_groups[i]}")

    top_idx = np.argmax(combined)
    insight = f"{labels[top_idx]}({combined[top_idx]:.1f}%) 직장인구가 가장 많아요."

    return {
        "상권코드": trdar_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 4. 유동인구 연령대
def plot_floating_gender_age_ratio(trdar_cd):
    df = df_flow[df_flow["상권_코드"] == trdar_cd].sort_values("기준_년분기_코드")
    if df.empty:
        return {"error": "해당 상권 데이터가 없습니다."}

    flow = df.iloc[-1]
    total = flow["총_유동인구_수"]

    age_groups = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
    age_cols = ["연령대_10_유동인구_수", "연령대_20_유동인구_수", "연령대_30_유동인구_수",
                "연령대_40_유동인구_수", "연령대_50_유동인구_수", "연령대_60_이상_유동인구_수"]

    # 남녀 분리 어려우므로 연령대 중심 분석
    age_pct = [flow[col] / total * 100 for col in age_cols]

    x = np.arange(len(age_groups))
    plt.figure(figsize=(10, 5))
    bars = plt.bar(x, age_pct, color='lightcoral')

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.3, f"{height:.1f}%", ha='center', fontsize=9)

    plt.ylabel("단위: %")
    plt.title("연령대별 유동인구 비율")
    plt.xticks(x, age_groups)
    plt.ylim(0, max(age_pct) + 5)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 저장
    fname = f"floating_age_{trdar_cd}"
    plt.savefig(make_img_path(fname))
    plt.close()

    # 인사이트 출력
    top_idx = np.argmax(age_pct)
    insight = f"{age_groups[top_idx]}({age_pct[top_idx]:.1f}%) 유동인구가 가장 많아요."

    return {
        "상권코드": trdar_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 5. 점포 수 추이
def plot_store_count_trend(trdar_cd, induty_cd):
    
    df = df_store[(df_store["상권_코드"] == trdar_cd) & 
                  (df_store["서비스_업종_코드"] == induty_cd)].sort_values("기준_년분기_코드")
    if df.empty:
        return {"error": "해당 상권/업종 데이터가 없습니다."}

    x = df["기준_년분기_코드"].astype(str)
    y = df["점포_수"]

    plt.figure(figsize=(10, 5))
    bars = plt.bar(x, y, color='gray')

    # 가장 최신 분기 색상 강조
    bars = list(bars)
    bars[-1].set_color("dodgerblue")

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 5, f"{int(height)}", ha='center', fontsize=9)

    plt.title("점포수 추이")
    plt.xlabel("기준 분기")
    plt.ylabel("점포 수")
    plt.ylim(0, max(y) + 10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 저장
    fname = f"store_count_{trdar_cd}_{induty_cd}"
    plt.savefig(make_img_path(fname))
    plt.close()

    # 인사이트 출력
    latest = df.iloc[-1]
    insight = f"최근 분기 점포 수: {int(latest['점포_수'])}개"

    if len(df) >= 2:
        delta_quarter = int(latest["점포_수"]) - int(df.iloc[-2]["점포_수"])
        sign = "▲" if delta_quarter > 0 else "▼"
        insight += f"\n   - 전분기 대비: {sign} {abs(delta_quarter)}개"

    if len(df) >= 5:
        delta_year = int(latest["점포_수"]) - int(df.iloc[-5]["점포_수"])
        sign = "▲" if delta_year > 0 else "▼"
        insight += f"\n   - 전년 동분기 대비: {sign} {abs(delta_year)}개"

    return {
        "상권코드": trdar_cd,
        "업종코드": induty_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 6. 개업 수 추이
def plot_open_store_trend(trdar_cd, induty_cd):
    df = df_store[(df_store["상권_코드"] == trdar_cd) & 
                  (df_store["서비스_업종_코드"] == induty_cd)].sort_values("기준_년분기_코드")
    if df.empty:
        return {"error": "해당 상권/업종 데이터가 없습니다."}

    x = df["기준_년분기_코드"].astype(str)
    y = df["개업_점포_수"]

    plt.figure(figsize=(10, 5))
    bars = plt.bar(x, y, color="lightgray")
    bars = list(bars)
    bars[-1].set_color("deepskyblue")

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 1, f"{int(height)}", ha='center', fontsize=9)

    plt.title("개업수 추이")
    plt.xlabel("분기")
    plt.ylabel("개업 점포 수")
    plt.ylim(0, max(y) + 10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()

    fname = f"store_open_{trdar_cd}_{induty_cd}"
    plt.savefig(make_img_path(fname))
    plt.close()

    # 인사이트 구성
    latest = df.iloc[-1]
    insight = f"최근 분기 개업수: {int(latest['개업_점포_수'])}개"

    if len(df) >= 2:
        delta_quarter = int(latest["개업_점포_수"]) - int(df.iloc[-2]["개업_점포_수"])
        sign = "▲" if delta_quarter > 0 else "▼"
        insight += f"\n   - 전분기 대비: {sign} {abs(delta_quarter)}개"

    if len(df) >= 5:
        delta_year = int(latest["개업_점포_수"]) - int(df.iloc[-5]["개업_점포_수"])
        sign = "▲" if delta_year > 0 else "▼"
        insight += f"\n   - 전년 동분기 대비: {sign} {abs(delta_year)}개"

    return {
        "상권코드": trdar_cd,
        "업종코드": induty_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 7. 폐업 수 추이
def plot_close_store_trend(trdar_cd, induty_cd):
    df = df_store[(df_store["상권_코드"] == trdar_cd) & 
                  (df_store["서비스_업종_코드"] == induty_cd)].sort_values("기준_년분기_코드")
    
    if df.empty:
        return {"error": "해당 상권/업종 데이터가 없습니다."}

    x = df["기준_년분기_코드"].astype(str)
    y = df["폐업_점포_수"]

    plt.figure(figsize=(10, 5))
    bars = plt.bar(x, y, color='lightgray')
    bars = list(bars)
    bars[-1].set_color("dodgerblue")

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 1, f"{int(height)}", ha='center', fontsize=9)

    plt.title("폐업수 추이")
    plt.xlabel("분기")
    plt.ylabel("폐업 점포 수")
    plt.ylim(0, max(y) + 10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()

    fname = f"store_close_{trdar_cd}_{induty_cd}"
    plt.savefig(make_img_path(fname))
    plt.close()

    # 인사이트 메시지 구성
    latest = df.iloc[-1]
    insight = f"최근 분기 폐업수: {int(latest['폐업_점포_수'])}개"

    if len(df) >= 2:
        delta_quarter = int(latest["폐업_점포_수"]) - int(df.iloc[-2]["폐업_점포_수"])
        sign = "▲" if delta_quarter > 0 else "▼"
        insight += f"\n   - 전분기 대비: {sign} {abs(delta_quarter)}개"

    if len(df) >= 5:
        delta_year = int(latest["폐업_점포_수"]) - int(df.iloc[-5]["폐업_점포_수"])
        sign = "▲" if delta_year > 0 else "▼"
        insight += f"\n   - 전년 동분기 대비: {sign} {abs(delta_year)}개"

    return {
        "상권코드": trdar_cd,
        "업종코드": induty_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 8. 프랜차이즈 비율
def plot_franchise_ratio(trdar_cd, induty_cd):
    df = df_store[(df_store["상권_코드"] == trdar_cd) & 
                  (df_store["서비스_업종_코드"] == induty_cd)].sort_values("기준_년분기_코드")
    
    if df.empty:
        return {"error": "해당 상권/업종 데이터가 없습니다."}

    latest = df.iloc[-1]
    total = latest["점포_수"]
    franchise = latest["프랜차이즈_점포_수"]
    general = total - franchise

    # 점포 수 없음 예외 처리
    if total == 0:
        return {"error": "해당 상권/업종에 점포 데이터가 없습니다."}

    values, labels, colors = [], [], []

    if general > 0:
        values.append(general)
        labels.append("일반점포")
        colors.append("dodgerblue")

    if franchise > 0:
        values.append(franchise)
        labels.append("프랜차이즈")
        colors.append("mediumseagreen")

    if not values:
        return {"error": "일반점포 및 프랜차이즈 점포 수가 모두 0입니다."}

    # 도넛 차트
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
        startangle=90,
        wedgeprops=dict(width=0.4),
        pctdistance=0.75,
        textprops={'fontsize': 11}
    )
    plt.setp(autotexts, color='black', weight='bold')
    ax.set_title("프랜차이즈와 일반 점포수 비교", pad=20)
    plt.tight_layout()

    # 저장
    fname = f"franchise_ratio_{trdar_cd}_{induty_cd}"
    plt.savefig(make_img_path(fname))
    plt.close()

    # 인사이트
    insight = f"프랜차이즈 비율: {franchise / total * 100:.1f}%"

    return {
        "상권코드": trdar_cd,
        "업종코드": induty_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 9. 남성 여성 고객 비율
def plot_gender_sales_ratio(trdar_cd, induty_cd):
    df = df_sales[(df_sales["상권_코드"] == trdar_cd) & 
                  (df_sales["서비스_업종_코드"] == induty_cd)].sort_values("기준_년분기_코드")
    
    if df.empty:
        return {"error": "해당 상권/업종 매출 데이터가 없습니다."}

    latest = df.iloc[-1]
    male_amt = latest["남성_매출_금액"]
    female_amt = latest["여성_매출_금액"]

    total = male_amt + female_amt
    if total == 0:
        return {"error": "해당 분기 매출 데이터가 없습니다."}

    male_pct = male_amt / total * 100
    female_pct = female_amt / total * 100

    labels = ["남성", "여성"]
    values = [male_pct, female_pct]
    colors = ["#00aaff", "#33cc99"]  # 원래 사용한 시각 색상 유지

    plt.figure(figsize=(6, 6))
    wedges, texts, autotexts = plt.pie(
        values, labels=labels, autopct="%.1f%%", startangle=90,
        colors=colors, pctdistance=0.8, wedgeprops=dict(width=0.4),
        textprops={'fontsize': 11}
    )
    plt.setp(autotexts, weight='bold', color='black')
    plt.title("성별 매출 현황", fontsize=14)
    plt.tight_layout()

    fname = f"sales_gender_{trdar_cd}_{induty_cd}"
    plt.savefig(make_img_path(fname))
    plt.close()

    target = "여성" if female_pct > male_pct else "남성"
    target_pct = max(female_pct, male_pct)

    return {
        "상권코드": trdar_cd,
        "업종코드": induty_cd,
        "인사이트": f"선택상권은 **{target}({target_pct:.1f}%)** 고객 비중이 높은 상권입니다.",
        "이미지URL": f"/static/img/{fname}.png"
    }

# 10. 시간별 매출
def plot_time_sales_ratio(trdar_cd, induty_cd):
    df = df_sales[(df_sales["상권_코드"] == trdar_cd) & 
                  (df_sales["서비스_업종_코드"] == induty_cd)].sort_values("기준_년분기_코드")

    if df.empty:
        return {"error": "해당 상권/업종 매출 데이터가 없습니다."}

    latest = df.iloc[-1]
    time_labels = ["00~06시", "06~11시", "11~14시", "14~17시", "17~21시", "21~24시"]
    time_cols = ["시간대_00~06_매출_금액", "시간대_06~11_매출_금액", "시간대_11~14_매출_금액",
                 "시간대_14~17_매출_금액", "시간대_17~21_매출_금액", "시간대_21~24_매출_금액"]
    
    time_sales = [latest[col] for col in time_cols]
    total = sum(time_sales)
    ratio = [s / total * 100 if total > 0 else 0 for s in time_sales]

    plt.figure(figsize=(10, 5))
    plt.plot(time_labels, ratio, marker="o", color="deepskyblue", linewidth=2)
    plt.fill_between(time_labels, ratio, alpha=0.3, color="skyblue")

    for x, y in zip(time_labels, ratio):
        plt.text(x, y + 1.5, f"{y:.1f}%", ha="center", fontsize=9)

    plt.title("🕒 시간대별 매출 비율")
    plt.ylabel("비율 (%)")
    plt.ylim(0, max(ratio) + 10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    fname = f"sales_time_{trdar_cd}_{induty_cd}"
    plt.savefig(make_img_path(fname))
    plt.close()

    max_idx = ratio.index(max(ratio))
    insight = f"{time_labels[max_idx]} 매출이 가장 많습니다. ({ratio[max_idx]:.1f}%)"

    return {
        "상권코드": trdar_cd,
        "업종코드": induty_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 11. 나이대별 고객 비율
def plot_age_sales_ratio(trdar_cd, induty_cd):
    df = df_sales[(df_sales["상권_코드"] == trdar_cd) & 
                  (df_sales["서비스_업종_코드"] == induty_cd)].sort_values("기준_년분기_코드")
    
    if df.empty:
        return {"error": "해당 상권/업종 매출 데이터가 없습니다."}

    latest = df.iloc[-1]
    age_labels = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
    age_cols = [f"연령대_{x}_매출_금액" for x in ["10", "20", "30", "40", "50", "60_이상"]]
    age_values = [latest[col] for col in age_cols]

    total = sum(age_values)
    age_pct = [v / total * 100 if total > 0 else 0 for v in age_values]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(age_labels, age_pct, color="lightgray")

    max_idx = age_pct.index(max(age_pct))
    bars[max_idx].set_color("dodgerblue")

    for i, bar in enumerate(bars):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 f"{age_pct[i]:.1f}%", ha='center', fontsize=9)

    plt.title("연령대별 매출 현황")
    plt.ylabel("비율 (%)")
    plt.ylim(0, max(age_pct) + 10)
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()

    fname = f"sales_age_{trdar_cd}_{induty_cd}"
    plt.savefig(make_img_path(fname))
    plt.close()

    max_age = age_labels[max_idx]
    max_val = age_pct[max_idx]

    return {
        "상권코드": trdar_cd,
        "업종코드": induty_cd,
        "인사이트": f"선택상권은 **{max_age}({max_val:.1f}%)** 소비자 매출 비중이 가장 높습니다.",
        "이미지URL": f"/static/img/{fname}.png"
    }

# 12. 점포 최근 분기 매출 추이
def plot_monthly_sales_per_store(trdar_cd, induty_cd):
    sales = df_sales[(df_sales["상권_코드"] == trdar_cd) & 
                     (df_sales["서비스_업종_코드"] == induty_cd)].sort_values("기준_년분기_코드")
    
    stores = df_store[(df_store["상권_코드"] == trdar_cd) & 
                      (df_store["서비스_업종_코드"] == induty_cd)][["기준_년분기_코드", "점포_수"]]
    
    df = pd.merge(sales, stores, on="기준_년분기_코드", how="left")
    df["점포당_월_매출"] = df["당월_매출_금액"] / df["점포_수"].replace(0, np.nan)
    df.dropna(subset=["점포당_월_매출"], inplace=True)
    
    if df.empty:
        return {"error": "점포당 매출 데이터가 없습니다."}

    df = df.sort_values("기준_년분기_코드")
    x = df["기준_년분기_코드"].astype(str)
    y = df["점포당_월_매출"] / 10000  # 만원 단위

    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o', color='deepskyblue', linewidth=2)

    for xi, yi in zip(x, y):
        plt.text(xi, yi + 10, f"{yi:.0f}", ha='center', fontsize=9)

    plt.title("점포당 월 평균 매출 추이 (선택 상권 기준)")
    plt.xlabel("분기")
    plt.ylabel("점포당 월 매출 (만원)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    fname = f"sales_monthly_{trdar_cd}_{induty_cd}"
    plt.savefig(make_img_path(fname))
    plt.close()

    # 인사이트 구성
    latest_amt = y.iloc[-1]
    insight = f"최근 분기 점포당 월 평균 매출: {int(latest_amt)}만원"

    if len(y) >= 2:
        delta_q = latest_amt - y.iloc[-2]
        sign = "▲" if delta_q > 0 else "▼"
        insight += f"\n   - 전분기 대비: {sign} {abs(int(delta_q))}만원"

    if len(y) >= 5:
        delta_y = latest_amt - y.iloc[-5]
        sign = "▲" if delta_y > 0 else "▼"
        insight += f"\n   - 전년 동분기 대비: {sign} {abs(int(delta_y))}만원"

    return {
        "상권코드": trdar_cd,
        "업종코드": induty_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 13. 상권 전체 업종 기준 점포당 월 매출 추이
def plot_avg_sales_per_store_by_area(trdar_cd):
    df = df_sales[df_sales["상권_코드"] == trdar_cd].copy()
    df_store_filtered = df_store[df_store["상권_코드"] == trdar_cd][["기준_년분기_코드", "서비스_업종_코드", "점포_수"]]

    df = df.merge(df_store_filtered, on=["기준_년분기_코드", "서비스_업종_코드"], how="left")
    df = df.sort_values("기준_년분기_코드")

    df["점포당_월_매출"] = df["당월_매출_금액"] / df["점포_수"].replace(0, np.nan)
    df.dropna(subset=["점포당_월_매출"], inplace=True)

    df_grouped = df.groupby("기준_년분기_코드")["점포당_월_매출"].mean().reset_index()
    if df_grouped.empty:
        return {"error": "해당 상권에 유효한 점포당 매출 데이터가 없습니다."}

    x = df_grouped["기준_년분기_코드"].astype(str)
    y = df_grouped["점포당_월_매출"] / 10000  # 만원 단위

    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o', color='mediumseagreen', linewidth=2)
    for xi, yi in zip(x, y):
        plt.text(xi, yi + 1, f"{yi:.0f}", ha='center', fontsize=9)

    plt.title("상권 전체 업종 기준 점포당 월 매출 추이")
    plt.xlabel("분기")
    plt.ylabel("점포당 월 매출 (만원)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    fname = f"avg_area_sales_{trdar_cd}"
    plt.savefig(make_img_path(fname))
    plt.close()

    # 인사이트 구성
    latest = y.iloc[-1]
    insight = f"최근 분기 전체 평균 점포당 월 매출: {int(latest)}만원"

    if len(y) >= 2:
        delta_q = latest - y.iloc[-2]
        sign = "▲" if delta_q > 0 else "▼"
        insight += f"\n   - 전분기 대비: {sign} {abs(int(delta_q))}만원"

    if len(y) >= 5:
        delta_y = latest - y.iloc[-5]
        sign = "▲" if delta_y > 0 else "▼"
        insight += f"\n   - 전년 동분기 대비: {sign} {abs(int(delta_y))}만원"

    return {
        "상권코드": trdar_cd,
        "인사이트": insight,
        "이미지URL": f"/static/img/{fname}.png"
    }

# 14. 상권 전체 업종 기준 점포당 월 매출 추이
def analyze_commercial_area(trdar_cd):
    # 데이터 준비
    pop = df_pop[df_pop["상권_코드"] == trdar_cd].sort_values("기준_년분기_코드")
    wrk = df_wrk[df_wrk["상권_코드"] == trdar_cd].sort_values("기준_년분기_코드")
    flow = df_flow[df_flow["상권_코드"] == trdar_cd].sort_values("기준_년분기_코드")

    if pop.empty or wrk.empty or flow.empty:
        return {"error": "상주/직장/유동 인구 데이터가 부족합니다."}

    # 상권 요약
    area_name = pop.iloc[-1]["상권_코드_명"]
    latest_data = {
        "상권명": area_name,
        "총_상주인구": int(pop.iloc[-1]["총_상주인구_수"]),
        "총_직장인구": int(wrk.iloc[-1]["총_직장_인구_수"]),
        "총_유동인구": int(flow.iloc[-1]["총_유동인구_수"]),
    }

    # 추세 그래프에 사용할 분기
    quarters = [20251, 20243, 20241, 20233, 20231, 20223]

    # 바 차트 함수

    def bar_plot(df, ycol, title, fname, color):
        df_sel = df[df["기준_년분기_코드"].isin(quarters)]
        
        # x축 값 (분기)
        x = df_sel["기준_년분기_코드"].astype(str).tolist()
        # y축 값 (해당 인구수 등)
        y = df_sel[ycol].tolist()
        
        plt.figure(figsize=(10, 4))
        plt.bar(x, y, color=color)
        plt.title(title)
        plt.xlabel("분기")
        plt.ylabel("인구 수")
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        
        path = make_img_path(fname)
        plt.savefig(path)
        plt.close()
        
        return f"/static/img/{fname}.png"

    # 개별 시각화 생성
    img_pop = bar_plot(pop, "총_상주인구_수", "총 상주인구 추세", f"pop_trend_{trdar_cd}", "gray")
    img_flow = bar_plot(flow, "총_유동인구_수", "총 유동인구 추세", f"flow_trend_{trdar_cd}", "lightcoral")
    img_wrk = bar_plot(wrk, "총_직장_인구_수", "총 직장인구 추세", f"wrk_trend_{trdar_cd}", "steelblue")

    # 결과 반환
    return {
        "상권요약": latest_data,
        "상주인구_그래프": img_pop,
        "유동인구_그래프": img_flow,
        "직장인구_그래프": img_wrk,
    }
    
def analyze_floating_time(trdar_cd: int):
    try:
        flow = df_flow[df_flow["상권_코드"] == trdar_cd].sort_values("기준_년분기_코드").iloc[-1]
        total = flow["총_유동인구_수"]

        time_labels = ["00~06시", "06~11시", "11~14시", "14~17시", "17~21시", "21~24시"]
        time_cols = ["시간대_00_06_유동인구_수", "시간대_06_11_유동인구_수", "시간대_11_14_유동인구_수",
                     "시간대_14_17_유동인구_수", "시간대_17_21_유동인구_수", "시간대_21_24_유동인구_수"]

        time_pct = [flow[col] / total * 100 for col in time_cols]
        top_idx = np.argmax(time_pct)
        insight = f"{time_labels[top_idx]} 유동인구가 가장 높아요. ({time_pct[top_idx]:.1f}%)"

        # 시각화
        plt.figure(figsize=(10, 5))
        plt.plot(time_labels, time_pct, marker="o", linewidth=3, color="deepskyblue")
        for i, v in enumerate(time_pct):
            plt.text(i, v + 0.8, f"{v:.1f}%", ha='center', fontsize=9)
        plt.ylim(0, max(time_pct) + 5)
        plt.title("시간대별 유동인구 현황")
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()

        img_path = os.path.join(IMG_DIR, f"floating_time_{trdar_cd}.png")
        plt.savefig(img_path)
        plt.close()

        return {
            "상권코드": trdar_cd,
            "인사이트": insight,
            "이미지URL": f"/static/floating_time_{trdar_cd}.png"
        }

    except Exception as e:
        return {"error": str(e)}