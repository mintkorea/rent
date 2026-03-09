
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

def change_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

def get_weekday_names(allow_day_str):
    if not allow_day_str: return ""
    days_map = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}
    day_list = [days_map.get(d.strip()) for d in allow_day_str.split(',') if d.strip() in days_map]
    return f"({','.join(day_list)})" if day_list else ""

# 2. CSS 스타일 (날짜 버튼 가로 정렬 + 카드 디테일 복구)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* [검색 버튼] 빨간색 원본 */
    div.stButton > button[kind="primary"] {
        background-color: #FF5252 !important; color: white !important;
        border-radius: 8px !important; height: 50px !important; font-weight: bold !important;
    }

    /* [날짜 박스] 버튼 가로 정렬을 위한 설정 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 15px; border: 1px solid #E1E8F0; margin: 20px 0;
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 15px; }
    
    /* 날짜 이동 버튼 (가로로 나란히 배치하기 위한 강제 스타일) */
    div[data-testid="stHorizontalBlock"] .stButton > button:not([kind="primary"]) {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 20px !important; font-weight: bold !important;
        border-radius: 4px !important; width: 50px !important; height: 40px !important;
        margin: 0 auto; display: block;
    }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; line-height: 40px; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* [카드 디자인] 스크린샷 18:57 완벽 복제 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 5px; margin-top: 25px; margin-bottom: 12px; display: flex; align-items: center; }
    .section-title { font-size: 17px; font-weight: bold; color: #444; margin: 15px 0 8px 0; display: flex; align-items: center; }
    
    .event-card { border: 1px solid #E8E8E8; border-left: 5px solid #1E3A5F; padding: 15px; border-radius: 8px; margin-bottom: 12px; background-color: white; position: relative; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    
    .status-badge { position: absolute; top: 15px; right: 15px; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; }
    .status-y { background-color: #FFF2E6; color: #FF8C00; } 
    .status-w { background-color: #E6F2FF; color: #007AFF; }
    
    .card-content { margin-top: 5px; }
    .place-name { font-size: 18px; font-weight: 800; color: #1E3A5F; margin-bottom: 5px; }
    .time-text { font-weight: bold; color: #E63946; font-size: 16px; margin-bottom: 3px; }
    .event-text { color: #333; font-size: 15px; margin-bottom: 5px; }
    
    /* 하단 정보 행 (날짜와 부서명 양끝 정렬) */
    .info-sub { font-size: 13px; color: #666; display: flex; justify-content: space-between; align-items: center; margin-top: 10px; border-top: 1px solid #F3F3F3; padding-top: 8px; }
    .info-sub span { display: flex; align-items: center; }

    /* TOP 버튼 및 하단 여백 */
    .top-floating {
        position: fixed; bottom: 25px; right: 20px; background-color: #1E3A5F;
        color: white !important; width: 50px; height: 50px; border-radius: 50%;
        text-align: center; line-height: 50px; font-weight: bold; z-index: 1000;
        text-decoration: none; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .footer-spacer { height: 100px; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 영역
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; color:#1E3A5F;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 메인 섹션 라벨 (아이콘 포함)
st.markdown('<div class="section-title">📅 날짜 선택</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<div class="section-title">🏢 건물 선택</div>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"sel_{b}")]

st.markdown('<div class="section-title">📋 대관 유형</div>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True
    components.html("<script>window.parent.document.getElementById('result-start').scrollIntoView({behavior:'smooth'});</script>", height=0)

# 4. 데이터 조회
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력 영역
if st.session_state.search_performed:
    st.markdown('<div id="result-start"></div>', unsafe_allow_html=True)
    df_raw = get_data(st.session_state.target_date)
    
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # [수정] 날짜 이동 박스 - 가로 정렬 강제 적용
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    cols = st.columns([1, 3, 1])
    with cols[0]:
        if st.button("⬅️", key="prev_btn"): change_date(-1); st.rerun()
    with cols[1]:
        st.markdown(f'<div style="text-align:center;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with cols[2]:
        if st.button("➡️", key="next_btn"): change_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    target_weekday = str(w_idx + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)]
            
            # 당일 대관
            if show_today:
                t_df = bu_df[bu_df['startDt'] == bu_df['endDt']]
                if not t_df.empty:
                    has_content = True
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, r in t_df.iterrows():
                        badge = f'<span class="status-badge status-y">예약확정</span>' if r.get('statNm')=='예약확정' else f'<span class="status-badge status-w">신청대기</span>'
                        st.markdown(f"""
                        <div class="event-card">{badge}
                            <div class="place-name">📍 {r['placeNm']}</div>
                            <div class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</div>
                            <div class="event-text">📄 {r['eventNm']}</div>
                            <div class="info-sub"><span>🗓️ {r['startDt']}</span><span>👥 {r.get('mgDeptNm','')}</span></div>
                        </div>""", unsafe_allow_html=True)

            # 기간 대관 (요일 표기 포함)
            if show_period:
                p_df = bu_df[(bu_df['startDt'] != bu_df['endDt']) & (bu_df['allowDay'].str.contains(target_weekday, na=False))]
                if not p_df.empty:
                    has_content = True
                    st.markdown('<div class="section-title">📅 기간 대관</div>', unsafe_allow_html=True)
                    for _, r in p_df.iterrows():
                        weekdays = get_weekday_names(r.get('allowDay',''))
                        st.markdown(f"""
                        <div class="event-card"><span class="status-badge status-
