import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# 1. 한국 시간 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

def is_holiday(d):
    holidays = [(1, 1), (3, 1), (5, 5), (6, 6), (8, 15), (10, 3), (10, 9), (12, 25)]
    return (d.month, d.day) in holidays

# 2. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state: st.session_state.target_date = today_kst()
if "search_performed" not in st.session_state: st.session_state.search_performed = False

# 3. CSS 스타일 (이미지 f1c9e3의 2단 박스 디자인 복구)
st.markdown("""
<style>
    .block-container { padding: 1.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 검색 결과 타이틀 (상단 박스) */
    .title-box {
        background-color: #F8FAFF;
        border: 1px solid #D1D9E6;
        border-radius: 10px 10px 0 0;
        padding: 10px;
        text-align: center;
        font-size: 18px;
        font-weight: 800;
        color: #1E3A5F;
        margin-top: 30px;
    }
    
    /* 날짜 표시 (하단 박스) */
    .date-display-box {
        background-color: #FFFFFF;
        border: 1px solid #D1D9E6;
        border-top: none;
        border-radius: 0 0 10px 10px;
        padding: 8px;
        text-align: center;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* 요일 색상 */
    .blue-date { color: #0047FF !important; }
    .red-date { color: #FF0000 !important; }
    .black-date { color: #333333 !important; }

    /* 슬림 내비게이션 버튼 */
    div[data-testid="stColumn"] button {
        height: 35px !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        background-color: #FFFFFF !important;
        border: 1px solid #D1D9E6 !important;
    }

    /* 카드 디자인 */
    .building-header { font-size: 18px; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 5px; margin: 25px 0 10px 0; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 6px; margin-bottom: 10px; background: white; line-height: 1.5; }
    .place-name { font-size: 16px; font-weight: 800; color: #1E3A5F; }
    .time-row { font-size: 15px; font-weight: 700; color: #D32F2F; margin-top: 3px; }
    .event-name { font-size: 14px; color: #444; margin-top: 5px; }
    .no-data-text { color: #999; font-size: 13px; padding: 15px; text-align: center; background: #FAFAFA; border: 1px dashed #DDD; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# 4. 상단 입력 영역 (건드리지 않음)
st.markdown('<h2 style="text-align:center;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

c_bu, c_ty = st.columns(2)
with c_bu:
    st.markdown('**🏢 건물 선택**')
    ALL_B = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
    selected_bu = [b for b in ALL_B if st.checkbox(b, value=(b=="성의회관"), key=f"cb_{b}")]
with c_ty:
    st.markdown('**🗓️ 유형 선택**')
    show_today = st.checkbox("당일 대관", value=True)
    show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 5. 데이터 함수
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 6. 결과 출력 (디자인 핵심)
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    
    # 요일 색상 판단
    c_cls = "black-date"
    if w_idx == 5: c_cls = "blue-date"
    elif w_idx == 6 or is_holiday(d): c_cls = "red-date"

    # [디자인] 상단 2단 박스 구조 (f1c9e3 복구)
    st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date-display-box {c_cls}">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)
    
    # [디자인] 하단 슬림 내비게이션: [ ◀ ] [ 오늘 ] [ ▶ ]
    nc1, nc2, nc3 = st.columns([1, 1.5, 1])
    with nc1:
        if st.button("◀", key="prev"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with nc2:
        if st.button("오늘", key="today"):
            st.session_state.target_date = today_kst()
            st.rerun()
    with nc3:
        if st.button("▶", key="next"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 데이터 매칭 및 출력 (기존 로직 유지)
    df_raw = get_data(d)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_any = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ","").str.contains(bu.replace(" ",""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: str(w_idx+1) in [i.strip() for i in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()
                
                combined = pd.concat([t_ev, v_p_ev]).sort_values(by='startTime')
                if not combined.empty:
                    has_any = True
                    for _, row in combined.iterrows():
                        st.markdown(f"""
                        <div class="event-card">
                            <div class="place-name">📍 {row['placeNm']}</div>
                            <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)
        if not has_any:
            st.markdown('<div class="no-data-text">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
