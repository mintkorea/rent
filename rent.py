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

# 3. CSS (줄간격 축소, 모바일 버튼 1열 고정, 탑버튼)
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 전체 줄간격 및 여백 축소 */
    p, div, label { margin-bottom: 2px !important; line-height: 1.1 !important; }
    .stCheckbox { margin-bottom: -5px !important; }

    /* 버튼 바: 모바일에서도 절대 한 줄 유지 */
    div[data-testid="stHorizontalBlock"] { gap: 0px !important; display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; }
    div[data-testid="column"] { min-width: 0px !important; flex: 1 1 auto !important; }
    
    div[data-testid="stHorizontalBlock"] button {
        height: 40px !important; border: 1px solid #D1D9E6 !important;
        background-color: white !important; border-radius: 0px !important; 
        width: 100% !important; margin: 0px !important; font-size: 16px !important;
    }
    div[data-testid="column"]:first-child button { border-radius: 8px 0 0 8px !important; border-right: none !important; }
    div[data-testid="column"]:last-child button { border-radius: 0 8px 8px 0 !important; border-left: none !important; }

    /* 카드 디자인 (f14301 참조) */
    .event-card { border:1px solid #E0E0E0; border-left:8px solid #2E5077; padding:8px 10px; border-radius:8px; margin-bottom:6px; background:white; position:relative; }
    .event-title { font-size:15px; font-weight:800; color:#1E3A5F; margin-bottom:2px; }
    .event-time { font-size:14px; font-weight:700; color:#D32F2F; margin-bottom:2px; }
    .event-desc { font-size:13px; color:#333; margin-bottom:5px; }
    .event-footer { border-top:1px solid #F0F0F0; padding-top:4px; display:flex; justify-content:space-between; font-size:11px; color:#666; }

    /* 탑버튼 */
    #target_result { scroll-margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# 4. 상단 입력 UI
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('**🏢 건물 선택**')
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"cb_{b}")]

# 대관 유형 선택 복구
st.markdown('**🗓️ 대관 유형 선택**')
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

# 검색 버튼 및 결과 이동 로직
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True
    st.markdown('<div id="target_result"></div>', unsafe_allow_html=True) # 결과 위치 앵커

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
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    c_cls = "red-date" if w_idx == 6 or is_holiday(d) else ("blue-date" if w_idx == 5 else "black-date")

    st.markdown(f'<div id="target_result" class="title-box" style="background:#F0F4FA; border:1px solid #D1D9E6; border-radius:12px 12px 0 0; padding:10px; text-align:center; font-weight:800; color:#1E3A5F;">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:white; border:1px solid #D1D9E6; border-top:none; border-radius:0 0 12px 12px; padding:10px; text-align:center; font-size:17px; font-weight:700; margin-bottom:5px;" class="{c_cls}">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)
    
    # 모바일 1줄 고정 버튼 바
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("◀", key="prev"): st.session_state.target_date -= timedelta(days=1); st.rerun()
    with c2:
        if st.button("오늘", key="today"): st.session_state.target_date = today_kst(); st.rerun()
    with c3:
        if st.button("▶", key="next"): st.session_state.target_date += timedelta(days=1); st.rerun()

    df_raw = get_data(st.session_state.target_date)
    for bu in selected_bu:
        st.markdown(f'<div style="font-size:15px; font-weight:bold; color:#1E3A5F; border-bottom:2px solid #1E3A5F; padding-bottom:2px; margin:15px 0 5px 0;">🏢 {bu}</div>', unsafe_allow_html=True)
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
                            <div class="event-title">📍 {row['placeNm']}</div>
                            <div class="event-time">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div class="event-desc">📄 {row['eventNm']}</div>
                            <div class="event-footer">
                                <span>📅 {date_info}</span>
                                <span>👤 {row.get('mgDeptNm', '정보없음')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        if not has_any:
            st.markdown('<div style="color:#999; font-size:12px; padding:10px; text-align:center; background:#FAFAFA; border:1px dashed #DDD; border-radius:10px;">내역 없음</div>', unsafe_allow_html=True)

    # 탑버튼 복구
    st.markdown('<br><a href="#target_result" style="display:block; text-align:center; color:#666; font-size:13px; text-decoration:none;">▲ 맨 위로 이동</a><br>', unsafe_allow_html=True)
