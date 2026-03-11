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

# 3. CSS (원본 디자인 유지 + 버튼 중앙 정렬 고정 + 플로팅 버튼)
st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 원본 줄간격 및 박스 디자인 유지 */
    div[data-testid="stVerticalBlock"] > div { padding: 0px !important; margin: 0px !important; }
    p, label { margin: 0px !important; line-height: 1.2 !important; }
    .stCheckbox { margin-bottom: -5px !important; }

    .title-box { background-color: #F0F4FA; border: 1px solid #D1D9E6; border-radius: 12px 12px 0 0; padding: 10px; text-align: center; font-weight: 800; color: #1E3A5F; margin-top: 10px; }
    .date-display-box { background-color: #FFFFFF; border: 1px solid #D1D9E6; border-top: none; border-radius: 0 0 12px 12px; padding: 10px; text-align: center; font-size: 18px; font-weight: 700; margin-bottom: 5px; }

    /* [해결] 버튼 세 개 강제 가로/중앙 정렬 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        gap: 8px !important;
        margin: 10px 0 !important;
    }
    [data-testid="column"] {
        width: auto !important;
        flex: 0 1 auto !important;
        min-width: 60px !important;
    }
    
    /* 카드 디자인 유지 */
    .event-card { border:1px solid #E0E0E0; border-left:8px solid #2E5077; padding:10px; border-radius:10px; margin-bottom:10px; background:white; position:relative; }
    .status-badge { position:absolute; top:10px; right:10px; background:#FFF3E0; color:#E65100; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:10px; }
    .event-footer { border-top:1px solid #F0F0F0; padding-top:6px; display:flex; justify-content:space-between; font-size:11px; color:#666; }

    /* 플로팅 탑버튼 스타일 */
    #floating-top-btn {
        position: fixed; bottom: 25px; right: 20px;
        background: #2E5077; color: white !important;
        width: 45px; height: 45px; border-radius: 50%;
        text-align: center; line-height: 45px; font-size: 20px;
        z-index: 999999; cursor: pointer; border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

# 4. 상단 입력부 (탑 앵커 추가)
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('**🏢 건물 선택**')
selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"] if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"cb_{b}")]

st.markdown('**🗓️ 대관 유형 선택**')
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True
    # 결과 위치로 자동 스크롤
    st.components.v1.html("<script>window.parent.document.getElementById('result-target').scrollIntoView({behavior:'smooth'});</script>", height=0)

# 5. 데이터 API
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 6. 결과 출력 영역
st.markdown('<div id="result-target"></div>', unsafe_allow_html=True)
if st.session_state.get("search_performed"):
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    c_cls = "red-date" if w_idx == 6 or is_holiday(d) else ("blue-date" if w_idx == 5 else "black-date")

    st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="date-display-box {c_cls}">{d.strftime("%Y.%m.%d")}.({w_str})</div>', unsafe_allow_html=True)
    
    # [수정] 중앙 정렬된 화살표 네비게이션
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("◀", key="prev_day"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with c2:
        if st.button("오늘", key="today_day"):
            st.session_state.target_date = today_kst()
            st.rerun()
    with c3:
        if st.button("▶", key="next_day"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    df_raw = get_data(st.session_state.target_date)
    for bu in selected_bu:
        st.markdown(f'<div style="font-size:16px; font-weight:bold; color:#1E3A5F; border-bottom:2px solid #1E3A5F; padding-bottom:3px; margin:15px 0 8px 0;">🏢 {bu}</div>', unsafe_allow_html=True)
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
                        st.markdown(f"""
                        <div class="event-card">
                            <div class="status-badge">예약확정</div>
                            <div style="font-size:16px; font-weight:800; color:#1E3A5F; margin-bottom:3px;">📍 {row['placeNm']}</div>
                            <div style="font-size:14px; font-weight:700; color:#D32F2F; margin-bottom:3px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:13px; color:#333; margin-bottom:8px;">📄 {row['eventNm']}</div>
                            <div class="event-footer"><span>📅 {row['startDt'] if row['startDt'] == row['endDt'] else row['startDt']+' ~ '+row['endDt']+allow_days}</span><span>👤 {row.get('mgDeptNm', '정보없음')}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
        if not has_any:
            st.markdown('<div style="color:#999; font-size:12px; padding:15px; text-align:center; background:#FAFAFA; border:1px dashed #DDD; border-radius:10px;">내역 없음</div>', unsafe_allow_html=True)

    # 플로팅 탑버튼 (JS를 활용해 부모 윈도우 스크롤 제어)
    st.components.v1.html("""
        <button id="floating-top-btn" onclick="window.parent.document.getElementById('top-anchor').scrollIntoView({behavior:'smooth'});">▲</button>
        <style>
            #floating-top-btn {
                position: fixed; bottom: 25px; right: 20px;
                background: #2E5077; color: white;
                width: 45px; height: 45px; border-radius: 50%;
                text-align: center; line-height: 45px; font-size: 20px;
                z-index: 999999; cursor: pointer; border: none;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }
        </style>
    """, height=0)
