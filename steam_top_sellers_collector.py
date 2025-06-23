import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# 한글 폰트 설정
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="Steam 인기 장르 분석", layout="wide")
st.title("\U0001F3AE Steam 인기 게임 장르 대시보드")

data_path = "data/steam_top_games_final.csv"

# 가격 문자열에서 숫자 추출
def extract_price(value):
    try:
        value = str(value).replace("₩", "").replace(",", "").strip()
        return float(value) if value else None
    except:
        return None

try:
    df = pd.read_csv(data_path)
    df["genres"] = df["genres"].apply(eval)

    # 사이드바
    with st.sidebar:
        st.header("\U0001F3DB️ 장르 및 가격 필터")
        all_genres = sorted({g for genre_list in df["genres"] for g in genre_list})
        selected_genres = st.multiselect("모든 장르 중에서 선택", all_genres, default=all_genres[:1])
        price_keyword = st.selectbox("가격 조건", ["모두 보기", "Free", "₩ 10,000 이하", "₩ 30,000 이하", "₩ 30,000 초과"])

    # 전체 장르 분석
    st.subheader("\U0001F4CA 전체 장르 분석")
    df_exploded = df.explode("genres")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### \U0001F4C9 장르별 게임 수 Top 10")
        genre_counts = df_exploded["genres"].value_counts().head(10)
        genre_counts = genre_counts.sort_values(ascending=True)
        st.bar_chart(genre_counts)

    with col2:
        st.markdown("#### ⭐ 장르별 평균 리뷰 수 Top 10")
        genre_reviews = df_exploded.groupby("genres")["reviews"].mean().sort_values(ascending=False).head(10)
        genre_reviews = genre_reviews.sort_values(ascending=True)
        st.bar_chart(genre_reviews)

    st.markdown("#### \U0001F9EE 장르별 게임 수 & 비율")
    col3, col4 = st.columns([2, 1])
    with col3:
        st.dataframe(genre_counts.reset_index().rename(columns={"index": "장르", "genres": "게임 수"}))
    with col4:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(genre_counts, labels=genre_counts.index, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        st.pyplot(fig)

    # 선택 장르 분석
    st.subheader(f"\U0001F50E 선택된 장르: {', '.join(selected_genres)}")
    st.caption("\U0001F4AC 참고: 가격 정보에는 DLC나 번들 상품 가격이 포함되어 있을 수 있습니다.")

    filtered_df = df[
        df["genres"].apply(lambda g: set(selected_genres).issubset(set(g))) &
        ~df["name"].str.contains("DLC|Pack|Soundtrack|Bundle|Upgrade|Add-on|Expansion|Season Pass|Content", case=False, na=False)
    ]

    # 가격 조건 필터링
    if price_keyword != "모두 보기":
        if "이하" in price_keyword or "초과" in price_keyword:
            threshold = int(price_keyword.replace("₩", "").replace(" 이하", "").replace(" 초과", ""))
            condition = (lambda x: extract_price(x) <= threshold) if "이하" in price_keyword else (lambda x: extract_price(x) > threshold)
            filtered_df = filtered_df[filtered_df["price"].apply(condition)]
        elif price_keyword == "Free":
            filtered_df = filtered_df[filtered_df["price"].str.contains("Free", na=False)]

    st.markdown(f"총 {len(filtered_df)}개 게임이 선택되었습니다.")

    if not filtered_df.empty:
        avg_reviews = int(filtered_df["reviews"].mean())
        prices = filtered_df["price"].apply(extract_price).dropna()
        avg_price = int(prices.mean()) if not prices.empty else 0

        rating_map = {
            "Overwhelmingly Positive": 100, "Very Positive": 90, "Positive": 80,
            "Mostly Positive": 75, "Mixed": 50, "Mostly Negative": 40,
            "Negative": 30, "Very Negative": 20, "Overwhelmingly Negative": 10
        }
        filtered_df["rating_score"] = filtered_df["rating"].map(rating_map)
        avg_rating_score = int(filtered_df["rating_score"].mean()) if not filtered_df["rating_score"].isna().all() else 0

        col5, col6, col7 = st.columns(3)
        col5.metric("\U0001F4C8 평균 리뷰 수", f"{avg_reviews:,} 개")
        col6.metric("\U0001F4B0 평균 가격(₩)", f"₩ {avg_price:,}" if not prices.empty else "정보 없음")
        col7.metric("⭐ 평균 평점 점수", f"{avg_rating_score}/100" if avg_rating_score else "정보 없음")

        filtered_df["price_value"] = filtered_df["price"].apply(extract_price).fillna(0)
        sorted_df = filtered_df.sort_values(by="price_value", ascending=False)

        st.dataframe(sorted_df[["name", "reviews", "rating", "price", "url"]], use_container_width=True)

except FileNotFoundError:
    st.warning(f"'{data_path}' 파일을 찾을 수 없습니다. 먼저 수집 스크립트를 실행해 주세요.")