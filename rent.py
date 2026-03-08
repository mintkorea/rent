import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: TOP 버튼 스타일 및 레이아웃
st.markdown("""
<style>
    .block-container { 
        padding: 1rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }

    /* 메인 타이틀 */
    .main-title {
        font-size: 24px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin-bottom: 5px !important; 
    }

    /* 검색 버튼 아래 여백 */
    div.stButton { margin-bottom: 35px !important; }

    /* 결과 타이틀 */
    .date-display { 
        text-align: center; font-size: 19px; font-weight: 800; 
        background-color: #F0F2F6; padding: 12px; border-radius: 10px; 
        margin-bottom: 20px; color: #1E3A5F;
    }

    /* 플로팅 TOP 버튼 (강제 노출 설정 포함) */
    #scrollToTopBtn {
        position: fixed;
        bottom: 40px;
        right: 20px;
        z-index: 999999;
        border: none;
        background-color: #1E3A5F;
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        cursor: pointer;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        line-height: 1;
    }
    #scrollToTopBtn:hover { background-color: #FF4B4B; }

    /* 카드/헤더 디자인 유지 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 15px 0 8px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 15px; border-radius: 5px; margin-bottom: 12px !important; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; }
    .status-badge { display: inline-block; padding: 2px 10px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    .place-time { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-highlight { color: #FF4B4B; margin-left: 8px; }
</style>
""", unsafe_allow_html=True)

# TOP 버튼 HTML (아이콘 추가)
st.markdown("""
    <button id="scrollToTopBtn" onclick="window.parent.window.scrollTo({top: 0, behavior: 'smooth'});">
        <span style="font-size:18px;">▲</span>
        <span>TOP</span>
    </button>
""", unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span style="font-size:18px; font-weight:800; color:#2E5077;">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span style="font-size:18px; font-weight:800; color:#2E5077;">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
cols = st.columns(2) # 체크박스를 2열로 배치하여 공간 절약
for i, b in enumerate(ALL_BUILDINGS):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v50_{b}"):
            selected_bu.append(b)

st.markdown('<span style="font-size:18px; font-weight:800; color:#2E5077;">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
col_t, col_p = st.columns(2)
with col_t: show_today = st.checkbox("당일 대관", value=True)
with col_p: show_period = st.checkbox("기간 대관", value=True)

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직 (생략 - 기존과 동일)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    p = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=p, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    st.markdown('<div id="result-section"></div>', unsafe_allow_html=True)
    df_raw = get_data(target_date)
    formatted_date = target_date.strftime("%Y.%m.%d")
    st.markdown(f'<div class="date-display">📋 성의교정 대관 현황({formatted_date})</div>', unsafe_allow_html=True)

    # 결과 스크롤 이동
    components.html(f"""<script>window.parent.document.getElementById("result-section").scrollIntoView({{behavior: "smooth", block: "start"}});</script>""", height=0)

    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]

        for bu in selected_bu:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()

            if bu_df.empty:
                st.markdown('<div style="color:#888; font-style:italic; padding:10px;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
            else:
                bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
                bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
                
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
                
                if show_today and not today_ev.empty:
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in today_ev.iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""<div class="event-card today-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div><div class="event-name">📄 {row['eventNm']}</div><div class="bottom-info">👥 {row['mgDeptNm']}</div></div>""", unsafe_allow_html=True)
                
                if show_period and not period_ev.empty:
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in period_ev.iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div><div class="event-name">📄 {row['eventNm']}</div><div class="bottom-info"><span class="period-label">🗓️ {row['startDt']} ~ {row['endDt']}</span> <span class="dept-label">👥 {row['mgDeptNm']}</span></div></div>""", unsafe_allow_html=True)
