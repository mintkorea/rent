import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

# 1. 한국 시간 및 공휴일 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

# 간단한 공휴일 체크 함수 (필요시 추가 가능)
def is_holiday(d):
    holidays = [
        (1, 1), (3, 1), (5, 5), (6, 6), (8, 15), (10, 3), (10, 9), (12, 25)
    ]
    return (d.month, d.day) in holidays

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state: st.session_state.target_date = today_kst()
if "search_performed" not in st.session_state: st.session_state.search_performed = False

# 2. CSS 스타일 (타이틀 박스 슬림화 + 요일 색상)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .main-title { font-size: 24px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 15px; }
    .sub-label { font-size: 16px; font-weight: 800; color: #2E5077; margin-top: 8px; display: block; }

    /* 결과 박스 슬림화 */
    .result-box-container {
        background-color: #F8FAFF;
        border: 1px solid #D1D9E6;
        border-radius: 10px;
        padding: 8px 5px; /* 패딩 축소 */
        text-align: center;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .result-title { font-size: 17px; font-weight: 800; color: #1E3A5F; margin-bottom: 5px; display: block; }
    
    /* 버튼 텍스트 색상 강제 지정 (요일용) */
    div[data-testid="stColumn"] button p { font-weight: 700 !important; font-size: 15px !important; }
    .blue-btn p { color: #0047FF !important; }
    .red-btn p { color: #FF0000 !important; }
    
    .building-header { font-size: 18px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 3px; margin: 12px 0 8px 0; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 5px; margin-bottom: 8px; background: white; line-height: 1.4; }
    .no-data-text { color: #999; font-size: 13px; padding: 12px; text-align: center; background: #fcfcfc; border: 1px dashed #ddd; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 영역
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
    ALL_BUILDINGS = ["성의회관", "의생명연구원", "옴니버스 파크", "대학본관"] # 예시 단축
    selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b=="성의회관"), key=f"c_{b}")]
with col_b:
    st.markdown('<span class="sub-label">🗓️ 유형 선택</span>', unsafe_allow_html=True)
    show_today = st.checkbox("당일 대관", value=True)
    show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터/요일 로직
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    st.markdown('<div id="result-top"></div>', unsafe_allow_html=True)
    
    # [디자인] 슬림한 결과 타이틀 박스
    st.markdown('<div class="result-box-container"><span class="result-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([0.8, 3, 0.8])
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    
    # 색상 클래스 결정
    color_class = ""
    if w_idx == 5: color_class = "blue-btn"
    elif w_idx == 6 or is_holiday(d): color_class = "red-btn"

    with c1:
        if st.button("◀", key="prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c2:
        # 요일 색상이 적용된 중앙 버튼
        if st.button(f"{d.strftime('%Y.%m.%d')}.({w_str})", key="curr", use_container_width=True, help="클릭 시 오늘로 이동"):
            st.session_state.target_date = today_kst()
            st.rerun()
        # CSS 주입으로 버튼 색상 변경
        if color_class:
            st.markdown(f'<style>div[data-testid="stHeaderActionElements"] + div div[data-testid="column"]:nth-child(2) button {{ border: 1px solid {"#0047FF" if color_class=="blue-btn" else "#FF0000"} !important; }}</style>', unsafe_allow_html=True)
            st.markdown(f'<div class="{color_class}"></div>', unsafe_allow_html=True) # 클래스 트리거용
    with c3:
        if st.button("▶", key="next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    df_raw = get_data(st.session_state.target_date)
    target_weekday = str(d.weekday() + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_bu_content = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_weekday in [d.strip() for d in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()

                # 카드 출력부
                for df in [t_ev, v_p_ev]:
                    if not df.empty:
                        has_bu_content = True
                        for _, row in df.sort_values(by='startTime').iterrows():
                            st.markdown(f"""<div class="event-card"><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div></div>""", unsafe_allow_html=True)

        if not has_bu_content:
            st.markdown('<div class="no-data-text">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
