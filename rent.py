import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [핵심] 세션 상태 초기화: 버튼 작동을 위해 중앙 집중식 날짜 관리
if 'target_date' not in st.session_state:
    st.session_state.target_date = date(2026, 3, 12)

# 요일 및 근무조 설정
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
WEEKDAY_MAP = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}

def get_shift_group(dt):
    """2026.01.01(B조) 기준 3교대 계산"""
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# CSS 스타일 정의 (image_82e95c.jpg 스타일 복구)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 16px !important; font-weight: 800; color: #2E5077; margin-top: 15px !important; display: block; margin-bottom: 5px; }
    .header-box {
        background-color: #F0F2F6; padding: 10px; border-radius: 8px;
        border: 1px solid #D1D9E6; text-align: center; font-weight: 800; font-size: 16px;
        width: 100%;
    }
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 15px; font-weight: bold; color: #444; margin: 15px 0 8px 0; padding-left: 8px; border-left: 5px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 10px !important; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .status-badge { float: right; padding: 2px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; background-color: #FFF4E5; color: #B25E09; }
    .time-highlight { color: #FF4B4B; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# 2. 상단 필터 영역 (image_9bde43.png 기반)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 선택 (세션 상태와 직접 연결)
st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
picked_date = st.date_input("날짜", value=st.session_state.target_date, key="date_picker", label_visibility="collapsed")
st.session_state.target_date = picked_date

# 건물 선택
st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
cols = st.columns(2)
for i, b in enumerate(ALL_BU):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_check_{i}"):
            selected_bu.append(b)

# 대관 유형 선택 복구
st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
t_col1, t_col2 = st.columns(2)
with t_col1: show_today = st.checkbox("당일 대관 보기", value=True, key="show_t")
with t_col2: show_period = st.checkbox("기간 대관 보기", value=True, key="show_p")

st.write(" ")
search_btn = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로드 함수
@st.cache_data(ttl=300)
def fetch_data(dt):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": dt.strftime('%Y-%m-%d'), "end": dt.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 화살표 버튼 및 결과 헤더 로직 (image_7fbaa4.png 스타일)
# 버튼 클릭 시 세션 상태를 변경하고 페이지를 즉시 재실행(rerun)
def move_date(offset):
    st.session_state.target_date += timedelta(days=offset)
    st.rerun()

st.write("---") # 구분선
c1, c2, c3 = st.columns([0.5, 4, 0.5])

with c1:
    if st.button("◀", key="btn_prev"):
        move_date(-1)

with c3:
    if st.button("▶", key="btn_next"):
        move_date(1)

with c2:
    curr = st.session_state.target_date
    w_idx = curr.weekday()
    # 요일별 색상: 토(청색), 일(적색), 평일(어두운 청색)
    t_color = "#0000FF" if w_idx == 5 else ("#FF0000" if w_idx == 6 else "#1E3A5F")
    shift = get_shift_group(curr)
    header_text = f"📋 현황 [ {curr.strftime('%Y.%m.%d')}({WEEKDAY_KR[w_idx]}) | {shift} ]"
    st.markdown(f'<div class="header-box" style="color:{t_color};">{header_text}</div>', unsafe_allow_html=True)

# 5. 대관 리스트 출력
df = fetch_data(st.session_state.target_date)
if not df.empty:
    target_weekday = str(st.session_state.target_date.weekday() + 1) # 1:월 ~ 7:일
    
    for bu in selected_bu:
        bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()
        if bu_df.empty: continue
        
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        
        # 당일 대관
        t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
        if show_today and not t_ev.empty:
            st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
            for _, row in t_ev.iterrows():
                st.markdown(f"""<div class="event-card"><span class="status-badge">예약확정</span><div>📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div><div class="event-name">📄 {row['eventNm']}</div><div class="info-row">👥 {row['mgDeptNm']}</div></div>""", unsafe_allow_html=True)

        # 기간 대관 (요일 필터링 적용)
        p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
        if show_period and not p_ev.empty:
            st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
            for _, row in p_ev.iterrows():
                allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                if target_weekday in allow_days:
                    days_list = [WEEKDAY_MAP.get(d) for d in allow_days if d in WEEKDAY_MAP]
                    wd_info = f"({', '.join(days_list)})"
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge">예약확정</span>
                        <div>📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                        <div class="event-name">📄 {row['eventNm']}</div>
                        <div class="info-row">
                            <span style="color:#d63384; font-weight:bold;">🗓️ {row['startDt']} ~ {row['endDt']} {wd_info}</span>
                            <span style="margin-left:8px; border-left:1px solid #ddd; padding-left:8px;">👥 {row['mgDeptNm']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("<br><center><a href='#v62_date' style='text-decoration:none; color:#1E3A5F; font-weight:bold;'>▲ 맨 위로 이동</a></center>", unsafe_allow_html=True)
