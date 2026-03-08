import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [세션 상태 관리] 날짜 및 결과 표시 트리거
if 'search_date' not in st.session_state:
    st.session_state.search_date = date(2026, 3, 12)
if 'triggered' not in st.session_state:
    st.session_state.triggered = False

# 요일 및 근무조 계산 로직
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
WEEKDAY_MAP = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}

def get_shift_group(dt):
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# CSS: 디자인 일체화 및 가독성 향상
st.markdown("""
<style>
    .block-container { padding: 1.5rem !important; max-width: 550px !important; }
    .main-title-text { font-size: 26px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 25px; }
    .sub-label { font-size: 16px; font-weight: 800; color: #2E5077; margin-top: 15px; display: block; margin-bottom: 5px; }
    
    /* 결과 타이틀 3분할 셀 디자인 */
    .nav-center-box {
        background-color: #F1F5F9;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        height: 58px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }
    
    /* 대관 카드 스타일 */
    .event-card { border: 1px solid #E2E8F0; border-left: 6px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 12px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .time-highlight { color: #FF4B4B; font-weight: 800; }
    .building-tag { font-size: 18px; font-weight: 800; color: #1E3A5F; margin-top: 25px; border-bottom: 2px solid #1E3A5F; padding-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# 2. 메인 타이틀 및 필터 영역 (상시 노출)
st.markdown('<div class="main-title-text">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 날짜 선택
st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
picked_date = st.date_input("날짜", value=st.session_state.search_date, label_visibility="collapsed")

# 건물 선택
st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [bu for bu in ALL_BU if st.checkbox(bu, value=(bu in ["성의회관", "의생명산업연구원"]))]

# 대관 유형 선택 (부활된 기능)
st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
c_type1, c_type2 = st.columns(2)
with c_type1: show_today = st.checkbox("당일 대관 보기", value=True)
with c_type2: show_period = st.checkbox("기간 대관 보기", value=True)

st.write(" ")
if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_date = picked_date
    st.session_state.triggered = True

# 3. 데이터 로드 함수
@st.cache_data(ttl=300)
def fetch_data(dt):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": dt.strftime('%Y-%m-%d'), "end": dt.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력 영역 (3개의 셀로 구성)
if st.session_state.triggered:
    st.markdown("---")
    
    # [핵심] 3개 셀 구조: 좌버튼 | 중앙 타이틀 | 우버튼
    col_l, col_c, col_r = st.columns([1, 4, 1])
    
    with col_l:
        st.write("##") # 수평 맞춤용 여백
        if st.button("◀", key="prev_day"):
            st.session_state.search_date -= timedelta(days=1)
            st.rerun()
            
    with col_c:
        curr = st.session_state.search_date
        w_idx = curr.weekday()
        t_color = "#FF0000" if w_idx == 6 else ("#0000FF" if w_idx == 5 else "#1E3A5F")
        shift = get_shift_group(curr)
        st.markdown(f"""
            <div class="nav-center-box">
                <div style="font-size: 14px; font-weight: 800; color: #1E3A5F;">📋 성의교정 대관 현황</div>
                <div style="font-size: 15px; font-weight: 700; color: {t_color};">
                    {curr.strftime('%Y.%m.%d')} ({WEEKDAY_KR[w_idx]}) | {shift}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_r:
        st.write("##") # 수평 맞춤용 여백
        if st.button("▶", key="next_day"):
            st.session_state.search_date += timedelta(days=1)
            st.rerun()

    # 데이터 표시 로직
    df = fetch_data(st.session_state.search_date)
    if not df.empty:
        target_wd = str(st.session_state.search_date.weekday() + 1)
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)]
            if bu_df.empty: continue
            
            # 건물별 결과 출력
            st.markdown(f'<div class="building-tag">🏢 {bu}</div>', unsafe_allow_html=True)
            
            for _, row in bu_df.iterrows():
                is_today = (row['startDt'] == row['endDt'])
                allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                
                # 당일/기간 필터 적용
                if (is_today and show_today) or (not is_today and show_period and target_wd in allow_days):
                    wd_info = f"<br><small style='color:#d63384;'>🗓️ 기간: {row['startDt']}~{row['endDt']}</small>" if not is_today else ""
                    st.markdown(f"""
                        <div class="event-card">
                            📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span><br>
                            📄 {row['eventNm']} {wd_info}
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("선택하신 날짜에 조회된 대관 내역이 없습니다.")

    st.markdown("<br><center><a href='#input_date' style='color:#999; font-size:13px; text-decoration:none;'>▲ 맨 위로 이동</a></center>", unsafe_allow_html=True)
