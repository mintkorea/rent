import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [기능] 날짜 변경 함수
def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (원본 카드 디자인 복구)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    div.stButton > button[kind="primary"] { background-color: #FF5252 !important; color: white !important; border-radius: 8px !important; height: 50px !important; font-weight: bold !important; }
    .date-display-box { text-align: center; background-color: #F8FAFF; padding: 20px 10px; border-radius: 15px; border: 1px solid #E1E8F0; margin-top: 20px; }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    div.stButton > button:not([kind="primary"]) { background-color: #A3D2F3 !important; border: none !important; color: white !important; font-size: 20px !important; font-weight: bold !important; border-radius: 5px !important; width: 60px !important; height: 45px !important; }
    .res-sub-title { font-size: 22px !important; font-weight: 700; color: #333; line-height: 45px; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .building-header { font-size: 20px !important; font-weight: bold; color: #1E3A5F; border-bottom: 3px solid #1E3A5F; padding-bottom: 8px; margin-top: 30px; margin-bottom: 15px; }
    .section-title { font-size: 18px; font-weight: bold; color: #444; margin: 20px 0 10px 0; }
    .event-card { border: 1px solid #E8E8E8; border-left: 6px solid #1E3A5F; padding: 15px; border-radius: 10px; margin-bottom: 12px; background-color: white; position: relative; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .status-badge { position: absolute; top: 15px; right: 15px; padding: 2px 12px; border-radius: 15px; font-size: 11px; font-weight: bold; }
    .status-y { background-color: #FFF2E6; color: #FF8C00; } 
    .status-w { background-color: #E6F2FF; color: #007AFF; }
    .place-name { font-size: 18px; font-weight: 800; color: #1E3A5F; margin-bottom: 8px; }
    .time-text { font-weight: bold; color: #E63946; }
    .info-sub { font-size: 13px; color: #666; display: flex; justify-content: space-between; margin-top: 10px; border-top: 1px solid #F0F0F0; padding-top: 8px; }
    .top-floating { position: fixed; bottom: 30px; right: 20px; background-color: #1E3A5F; color: white !important; width: 50px; height: 50px; border-radius: 50%; text-align: center; line-height: 50px; font-weight: bold; z-index: 1000; text-decoration: none; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# 3. 입력부
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏢 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

st.session_state.target_date = st.date_input("날짜 선택", value=st.session_state.target_date)
selected_bu = [b for b in ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"] if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]))]
show_today = st.checkbox("📌 당일 대관", value=True)
show_period = st.checkbox("🗓️ 기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True
    components.html("<script>window.parent.document.getElementById('result-start').scrollIntoView({behavior:'smooth'});</script>", height=0)

# 4. 데이터 로직 (KeyError 방지용 컬럼 체크 추가)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        data = res.json().get('res', [])
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    st.markdown('<div id="result-start"></div>', unsafe_allow_html=True)
    df_raw = get_data(st.session_state.target_date)
    
    # 필수 컬럼이 없을 경우 빈 DataFrame으로 처리하여 KeyError 방지
    required_cols = ['buNm', 'placeNm', 'startTime', 'endTime', 'eventNm', 'startDt', 'endDt']
    for col in required_cols:
        if not df_raw.empty and col not in df_raw.columns:
            df_raw[col] = ""

    d = st.session_state.target_date
    w_str = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]
    w_class = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")

    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("⬅️", key="p_btn"): change_date(-1); st.rerun()
    with c2:
        st.markdown(f'<div style="text-align:center;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with c3:
        if st.button("➡️", key="n_btn"): change_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    target_weekday = str(d.weekday() + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_bu_content = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)]
            
            # 당일 대관 로직
            if show_today:
                t_df = bu_df[bu_df['startDt'] == bu_df['endDt']]
                if not t_df.empty:
                    has_bu_content = True
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, r in t_df.iterrows():
                        status_class = "status-y" if r.get('statNm', '') == '예약확정' else "status-w"
                        status_name = r.get('statNm', '예약확정')
                        st.markdown(f"""
                        <div class="event-card"><span class="status-badge {status_class}">{status_name}</span>
                            <div class="place-name">📍 {r['placeNm']}</div>
                            <div class="card-row"><span class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</span></div>
                            <div class="card-row">📄 {r['eventNm']}</div>
                            <div class="info-sub"><span>🗓️ {r['startDt']}</span><span>👥 {r.get('mgDeptNm', '정보 없음')}</span></div>
                        </div>""", unsafe_allow_html=True)

            # 기간 대관 로직
            if show_period:
                p_df = bu_df[(bu_df['startDt'] != bu_df['endDt']) & (bu_df['allowDay'].str.contains(target_weekday, na=False))]
                if not p_df.empty:
                    has_bu_content = True
                    st.markdown('<div class="section-title">📅 기간 대관</div>', unsafe_allow_html=True)
                    for _, r in p_df.iterrows():
                        st.markdown(f"""
                        <div class="event-card"><span class="status-badge status-y">예약확정</span>
                            <div class="place-name">📍 {r['placeNm']}</div>
                            <div class="card-row"><span class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</span></div>
                            <div class="card-row">📄 {r['eventNm']}</div>
                            <div class="info-sub"><span>🗓️ {r['startDt']} ~ {r['endDt']}</span><span>👥 {r.get('mgDeptNm', '정보 없음')}</span></div>
                        </div>""", unsafe_allow_html=True)
        
        if not has_bu_content:
            st.markdown('<div style="color:gray; padding:10px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

st.markdown('<a href="#top-anchor" class="top-floating">TOP</a>', unsafe_allow_html=True)
