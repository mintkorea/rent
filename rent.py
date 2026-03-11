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

# 3. CSS (줄간격 축소, 타이틀박스 너비 버튼, 플로팅 탑버튼)
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 줄간격 최소화 */
    div[data-testid="stVerticalBlock"] > div { padding-top: 0px !important; padding-bottom: 2px !important; }
    p, label { margin-bottom: 0px !important; line-height: 1.1 !important; }

    /* 타이틀 및 날짜 박스 */
    .title-box { background-color: #F0F4FA; border: 1px solid #D1D9E6; border-radius: 12px 12px 0 0; padding: 10px; text-align: center; font-weight: 800; color: #1E3A5F; }
    .date-display-box { background-color: #FFFFFF; border: 1px solid #D1D9E6; border-top: none; border-radius: 0 0 12px 12px; padding: 10px; text-align: center; font-size: 17px; font-weight: 700; }
    
    /* 버튼 바: 타이틀 박스 너비에 맞춤 및 한 줄 유지 */
    .nav-container { display: flex !important; width: 100% !important; gap: 0px !important; margin-top: 5px; }
    div[data-testid="stHorizontalBlock"] { gap: 0px !important; display: flex !important; flex-wrap: nowrap !important; }
    div[data-testid="stHorizontalBlock"] button {
        height: 38px !important; border: 1px solid #D1D9E6 !important;
        background-color: white !important; border-radius: 0px !important; 
        width: 100% !important; margin: 0px !important; font-size: 14px !important;
    }
    div[data-testid="column"]:first-child button { border-radius: 8px 0 0 8px !important; border-right: none !important; }
    div[data-testid="column"]:last-child button { border-radius: 0 8px 8px 0 !important; border-left: none !important; }

    /* 플로팅 탑버튼 */
    .floating-top { position: fixed; bottom: 20px; right: 20px; z-index: 999; background: #2E5077; color: white; padding: 10px; border-radius: 50%; width: 40px; height: 40px; text-align: center; text-decoration: none; font-size: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }

    /* 카드 디자인 */
    .event-card { border:1px solid #E0E0E0; border-left:8px solid #2E5077; padding:10px; border-radius:8px; margin-bottom:6px; background:white; position:relative; }
    .event-footer { border-top:1px solid #F0F0F0; padding-top:5px; display:flex; justify-content:space-between; font-size:11px; color:#666; }
</style>
""", unsafe_allow_html=True)

# 4. 상단 입력부
st.markdown('<h3 style="text-align:center; margin-bottom:5px;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('**🏢 건물 선택**')
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"cb_{b}")]

st.markdown('**🗓️ 대관 유형 선택**')
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True
    # 결과 위치로 앵커 이동
    st.markdown('<script>window.location.hash="target_anchor";</script>', unsafe_allow_html=True)

# 5. 데이터 API
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 6. 결과 출력
if st.session_state.get("search_performed"):
    st.markdown('<div id="target_anchor"></div>', unsafe_allow_html=True)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    c_cls = "red-date" if w_idx == 6 or is_holiday(d) else ("blue-date" if w_idx == 5 else "black-date")

    st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date-display-box {c_cls}">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)
    
    # 버튼 바 (타이틀 박스 너비에 맞게 한 줄로)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("◀", key="p_btn"): st.session_state.target_date -= timedelta(days=1); st.rerun()
    with c2:
        if st.button("오늘", key="t_btn"): st.session_state.target_date = today_kst(); st.rerun()
    with c3:
        if st.button("▶", key="n_btn"): st.session_state.target_date += timedelta(days=1); st.rerun()

    df_raw = get_data(st.session_state.target_date)
    for bu in selected_bu:
        st.markdown(f'<div style="font-size:15px; font-weight:bold; color:#1E3A5F; border-bottom:2px solid #1E3A5F; padding-bottom:2px; margin-top:10px;">🏢 {bu}</div>', unsafe_allow_html=True)
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
                        days_map = {'1':'월','2':'화','3':'수','4':'목','5':'금','6':'토','7':'일'}
                        allow_days = f" ({','.join([days_map[i.strip()] for i in str(row['allowDay']).split(',') if i.strip() in days_map])})" if row['startDt'] != row['endDt'] else ""
                        date_info = f"{row['startDt']} ~ {row['endDt']}{allow_days}" if row['startDt'] != row['endDt'] else row['startDt']

                        st.markdown(f"""
                        <div class="event-card">
                            <div style="position:absolute; top:8px; right:10px; background:#FFF3E0; color:#E65100; font-size:10px; font-weight:bold; padding:1px 6px; border-radius:10px;">예약확정</div>
                            <div style="font-size:15px; font-weight:800; color:#1E3A5F; margin-bottom:2px;">📍 {row['placeNm']}</div>
                            <div style="font-size:14px; font-weight:700; color:#D32F2F; margin-bottom:2px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:13px; color:#333; margin-bottom:5px;">📄 {row['eventNm']}</div>
                            <div class="event-footer">
                                <span>📅 {date_info}</span>
                                <span>👤 {row.get('mgDeptNm', '정보없음')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        if not has_any:
            st.markdown('<div style="color:#999; font-size:12px; padding:10px; text-align:center; background:#FAFAFA; border:1px dashed #DDD; border-radius:10px;">내역 없음</div>', unsafe_allow_html=True)

    # 결과 하단 여백 및 플로팅 탑버튼
    st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
    st.markdown('<a href="#" class="floating-top">▲</a>', unsafe_allow_html=True)
