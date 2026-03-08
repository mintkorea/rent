import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 이전의 깔끔한 스타일로 복구 + 타이틀 박스 강제 합병
st.markdown("""
<style>
    .block-container { padding: 0.5rem 0.8rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    
    /* 회색 배경 박스 */
    .filter-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }

    /* 박스 안으로 들어갈 타이틀 스타일 */
    .inner-box-title {
        font-size: 22px !important;
        font-weight: 800 !important;
        text-align: center;
        color: #1E3A5F;
        margin-bottom: 15px !important;
        padding-bottom: 10px;
        border-bottom: 1px solid #dee2e6;
    }

    /* 결과 타이틀 박스 (슬림) */
    .result-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 8px !important;
        text-align: center;
        margin-bottom: 15px;
    }

    .sub-header {
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #2E5077;
        margin-top: 10px !important;
        display: block;
    }

    /* 체크박스 가로 배열 복구 */
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. 메인 필터 영역
# [수정] 박스를 먼저 열고, 그 안에서 모든 것을 순서대로 배치합니다.
st.markdown('<div class="filter-container">', unsafe_allow_html=True)

# 메인 타이틀 (이제 확실히 박스 안에 포함됨)
st.markdown('<div class="inner-box-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-header">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-header">🏢 건물 선택</span>', unsafe_allow_html=True)
all_b = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_buildings = []
for b in all_b:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"cb_{b}"):
        selected_buildings.append(b)

st.markdown('<span class="sub-header">🗓️ 대관 유형</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관", value=True)
with c2: show_period = st.checkbox("기간 대관", value=False)

st.write("")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True) # 박스 닫기

# 3. 데이터 함수
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    p = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=p, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    df = pd.DataFrame()
    if not df_raw.empty:
        temp = df_raw.copy()
        temp['s_dt'] = pd.to_datetime(temp['startDt']).dt.date
        temp['e_dt'] = pd.to_datetime(temp['endDt']).dt.date
        df = temp[(temp['s_dt'] <= target_date) & (temp['e_dt'] >= target_date)]

    st.write("")
    
    # 결과 타이틀 박스
    f_date = target_date.strftime('%m/%d')
    st.markdown(f"""
    <div class="result-box">
        <span style="font-size: 19px; font-weight: 800; color: #1E3A5F;">
            🏢 성의교정 대관 현황({f_date})
        </span>
    </div>
    """, unsafe_allow_html=True)

    for bu in selected_buildings:
        st.markdown(f'<div style="font-size:18px; font-weight:bold; color:#2E5077; margin-top:12px; border-bottom:2px solid #2E5077;">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df[df['buNm'].str.contains(bu, na=False)].copy() if not df.empty else pd.DataFrame()
        
        if bu_df.empty:
            st.markdown('<div style="color:#888; font-size:14px; padding:5px 0;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
        else:
            bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            for _, row in bu_df.iterrows():
                is_p = row['startDt'] != row['endDt']
                if (is_p and not show_period) or (not is_p and not show_today): continue
                st.markdown(f"""
                <div style="border:1px solid #E0E0E0; border-left:5px solid #2E5077; padding:8px; border-radius:6px; margin-bottom:6px; background-color:#ffffff;">
                    <b>📍 {row["placeNm"]}</b> ({"확정" if row['status'] == 'Y' else "대기"})<br>
                    <span style="color:#FF4B4B;">⏰ {row["startTime"]}~{row["endTime"]}</span>
                    {"<br><span style='font-size:12px; color:#d63384;'>🗓️ "+row['startDt']+"~"+row['endDt']+"</span>" if is_p else ""}<br>
                    <span style="font-size:14px;">📄 {row["eventNm"]}</span>
                </div>
                """, unsafe_allow_html=True)
