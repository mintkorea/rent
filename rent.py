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

if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()
if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

# 3. CSS 스타일 (기존 성공 디자인 100% 유지 + 버튼 슬림화)
st.markdown("""
<style>
    .block-container { padding: 1.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* [기존 디자인] 타이틀 박스 */
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
    
    /* [기존 디자인] 날짜 박스 */
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

    /* 요일 색상 로직 */
    .blue-date { color: #0047FF !important; }
    .red-date { color: #FF0000 !important; }
    .black-date { color: #333333 !important; }

    /* [추가] 슬림 버튼 중앙 정렬 스타일 */
    .nav-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    div[data-testid="stColumn"] button {
        height: 30px !important;
        min-height: 30px !important;
        padding: 0px 10px !important;
        font-size: 13px !important;
        line-height: 30px !important;
        border-radius: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. 상단 입력 영역 (원본 유지)
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

# 5. 데이터 함수 (원본 유지)
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 6. 결과 출력
if st.session_state.search_performed:
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    
    # 요일 색상 설정
    c_cls = "black-date"
    if w_idx == 5: c_cls = "blue-date"
    elif w_idx == 6 or is_holiday(d): c_cls = "red-date"

    # [디자인] 기존 성공 디자인 박스
    st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date-display-box {c_cls}">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)
    
    # [디자인] 버튼 3개 슬림하게 중앙 정렬
    bc1, bc2, bc3, bc4, bc5 = st.columns([1, 1, 1.2, 1, 1])
    with bc2:
        if st.button("◀", key="prev", use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with bc3:
        if st.button("오늘", key="today", use_container_width=True):
            st.session_state.target_date = today_kst()
            st.rerun()
    with bc4:
        if st.button("▶", key="next", use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    # 데이터 출력부 (원본 로직 유지)
    df_raw = get_data(d)
    for bu in selected_bu:
        st.markdown(f'<div style="font-size:18px; font-weight:bold; color:#1E3A5F; border-bottom:2px solid #1E3A5F; padding-bottom:5px; margin:25px 0 10px 0;">🏢 {bu}</div>', unsafe_allow_html=True)
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
                        <div style="border:1px solid #E0E0E0; border-left:5px solid #2E5077; padding:12px; border-radius:6px; margin-bottom:10px; background:white;">
                            <div style="font-size:16px; font-weight:800; color:#1E3A5F;">📍 {row['placeNm']}</div>
                            <div style="font-size:15px; font-weight:700; color:#D32F2F; margin-top:3px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:14px; color:#444; margin-top:5px;">📄 {row['eventNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)
        if not has_any:
            st.markdown('<div style="color:#999; font-size:13px; padding:15px; text-align:center; background:#FAFAFA; border:1px dashed #DDD; border-radius:10px;">조회된 대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
