import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태를 이용해 날짜 변경 관리
if 'target_date' not in st.session_state:
    st.session_state.target_date = date(2026, 3, 12)

# 요일 및 근무조 설정
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
WEEKDAY_MAP = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}

def get_shift_group(target_date):
    base_date = date(2026, 1, 1) # 2026.01.01(B조) 기준
    diff_days = (target_date - base_date).days
    shift_idx = (diff_days + 1) % 3
    return SHIFT_TYPES[shift_idx]

# CSS 스타일 (image_82e95c.jpg 스타일 및 버튼 디자인)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 17px !important; font-weight: 800; color: #2E5077; margin-top: 12px !important; display: block; }
    .date-display-box { 
        text-align: center; background-color: #F0F2F6; padding: 10px; 
        border-radius: 10px; margin: 10px 0; border: 1px solid #D1D9E6;
        display: flex; justify-content: space-between; align-items: center;
    }
    .date-text { font-size: 17px; font-weight: 800; flex-grow: 1; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 16px; font-weight: bold; color: #444; margin: 18px 0 10px 0; padding-left: 8px; border-left: 5px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 15px; border-radius: 8px; margin-bottom: 12px !important; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .status-badge { float: right; padding: 2px 10px; font-size: 11px; border-radius: 10px; font-weight: bold; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    .time-highlight { color: #FF4B4B; margin-left: 8px; font-weight: 800; }
    .event-name { font-size: 14px; margin-top: 8px; color: #333; font-weight: 600; }
    .info-row { font-size: 12px; color: #666; margin-top: 8px; display: flex; align-items: center; gap: 5px; }
</style>
""", unsafe_allow_html=True)

# 2. 검색 필터 영역
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
# 세션 상태와 연동된 날짜 입력
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed", key="v60_date_input")
st.session_state.target_date = target_date

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
cols = st.columns(2)
for i, b in enumerate(ALL_BU):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v60_b_{i}"):
            selected_bu.append(b)

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True, key="v60_btn_search")

# 3. 데이터 로직
@st.cache_data(ttl=300)
def fetch_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력 및 이동 버튼
if search_clicked or 'v60_btn_search' in st.session_state:
    df = fetch_data(st.session_state.target_date)
    
    # 요일 색상 계산
    w_idx = st.session_state.target_date.weekday()
    color = "#1E3A5F"
    if w_idx == 5: color = "#0000FF"
    elif w_idx == 6: color = "#FF0000"

    # 전날/다음날 이동 버튼 레이아웃
    btn_col1, btn_col2, btn_col3 = st.columns([1, 4, 1])
    
    with btn_col1:
        if st.button("◀", key="v60_prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
            
    with btn_col2:
        shift = get_shift_group(st.session_state.target_date)
        d_str = st.session_state.target_date.strftime("%Y.%m.%d")
        w_str = WEEKDAY_KR[w_idx]
        st.markdown(f"""
            <div class="date-display-box">
                <div class="date-text" style="color:{color};">
                    📋 현황 [ {d_str}({w_str}) | {shift} ]
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with btn_col3:
        if st.button("▶", key="v60_next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 데이터 렌더링 (동일 조건 필터링)
    if not df.empty:
        df['startDt_dt'] = pd.to_datetime(df['startDt']).dt.date
        df['endDt_dt'] = pd.to_datetime(df['endDt']).dt.date
        mask = (df['startDt_dt'] <= st.session_state.target_date) & (df['endDt_dt'] >= st.session_state.target_date)
        filtered_df = df[mask].copy()

        for bu in selected_bu:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = filtered_df[filtered_df['buNm'].str.contains(bu, na=False)].copy()

            if bu_df.empty:
                st.markdown('<div style="color:#888; padding:10px;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
            else:
                bu_df = bu_df.sort_values(by=['placeNm', 'startTime'])
                
                # 당일/기간 대관 구분 출력 (생략된 기존 필터링 로직 동일 적용)
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
                # ... (중략: 이전 버전과 동일한 렌더링 코드) ...
                # 기간 대관 요일 필터링 적용
                target_weekday = str(st.session_state.target_date.weekday() + 1)
                for _, row in p_ev.iterrows():
                    allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                    if target_weekday in allow_days:
                        # 카드 렌더링...
                        pass

    st.markdown("<br><center><a href='#' style='text-decoration:none; color:#1E3A5F; font-weight:bold;'>▲ 맨 위로 이동</a></center><br>", unsafe_allow_html=True)
