import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date(2026, 3, 12)

# 요일 및 근무조 설정
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
WEEKDAY_MAP = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}

def get_shift_group(dt):
    base_date = date(2026, 1, 1) # 2026.01.01(B조) 기준
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# CSS 스타일 유지 (image_82e95c.jpg 스타일)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 16px !important; font-weight: 800; color: #2E5077; margin-top: 15px !important; display: block; margin-bottom: 5px; }
    .header-box {
        background-color: #F0F2F6; padding: 10px; border-radius: 8px;
        border: 1px solid #D1D9E6; text-align: center; font-weight: 800; font-size: 16px;
    }
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 15px; font-weight: bold; color: #444; margin: 15px 0 8px 0; padding-left: 8px; border-left: 5px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 10px !important; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .status-badge { float: right; padding: 2px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; background-color: #FFF4E5; color: #B25E09; }
    .time-text { font-size: 15px; font-weight: bold; color: #1E3A5F; }
    .time-highlight { color: #FF4B4B; }
    .event-name { font-size: 14px; margin-top: 5px; color: #333; font-weight: 600; }
    .info-row { font-size: 12px; color: #666; margin-top: 5px; display: flex; align-items: center; gap: 8px; }
</style>
""", unsafe_allow_html=True)

# 2. 상단 검색 필터 (image_9bde43.png 디자인 반영)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
new_date = st.date_input("date_in", value=st.session_state.target_date, label_visibility="collapsed", key="v62_date")
st.session_state.target_date = new_date

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
cols = st.columns(2)
for i, b in enumerate(ALL_BU):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v62_bu_{i}"):
            selected_bu.append(b)

# 사라졌던 대관 유형 선택 부분 복구
st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
type_cols = st.columns(2)
with type_cols[0]:
    show_today = st.checkbox("당일 대관 보기", value=True, key="v62_show_today")
with type_cols[1]:
    show_period = st.checkbox("기간 대관 보기", value=True, key="v62_show_period")

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True, key="v62_search_btn")

# 3. 데이터 로드 함수
@st.cache_data(ttl=300)
def fetch_data(dt):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": dt.strftime('%Y-%m-%d'), "end": dt.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked or 'v62_search_btn' in st.session_state:
    # 이동 버튼 및 헤더
    c1, c2, c3 = st.columns([0.5, 3, 0.5])
    with c1:
        if st.button("◀", key="v62_prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c3:
        if st.button("▶", key="v62_next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()
    with c2:
        curr = st.session_state.target_date
        w_idx = curr.weekday()
        t_color = "#0000FF" if w_idx == 5 else ("#FF0000" if w_idx == 6 else "#1E3A5F")
        shift = get_shift_group(curr)
        st.markdown(f'<div class="header-box" style="color:{t_color};">📋 현황 [ {curr.strftime("%Y.%m.%d")}({WEEKDAY_KR[w_idx]}) | {shift} ]</div>', unsafe_allow_html=True)

    df = fetch_data(st.session_state.target_date)
    if not df.empty:
        # 요일 필터값 (1:월 ~ 7:일)
        target_weekday = str(st.session_state.target_date.weekday() + 1)
        
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            
            # 당일 대관 필터링 및 출력
            today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
            if show_today and not today_ev.empty:
                st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                for _, row in today_ev.iterrows():
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge">예약확정</span>
                        <div class="time-text">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                        <div class="event-name">📄 {row['eventNm']}</div>
                        <div class="info-row">👥 {row['mgDeptNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # 기간 대관 필터링(요일 체크 포함) 및 출력
            period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
            if show_period and not period_ev.empty:
                st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                for _, row in period_ev.iterrows():
                    allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                    if target_weekday in allow_days:
                        days_list = [WEEKDAY_MAP.get(d) for d in allow_days if d in WEEKDAY_MAP]
                        wd_info = f"({', '.join(days_list)})"
                        st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge">예약확정</span>
                            <div class="time-text">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                            <div class="info-row">
                                <span style="color:#d63384; font-weight:bold;">🗓️ {row['startDt']} ~ {row['endDt']} {wd_info}</span>
                                <span style="margin-left:8px; border-left:1px solid #ddd; padding-left:8px;">👥 {row['mgDeptNm']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    st.markdown("<br><center><a href='#' style='text-decoration:none; color:#1E3A5F; font-weight:bold;'>▲ 맨 위로 이동</a></center>", unsafe_allow_html=True)
