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

# 2. CSS 스타일 (타이틀 축소 + 카드 줄간격 최적화)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* [1] 메인 페이지 타이틀 수정: 크기 축소 및 줄간격(margin) 조정 */
    .main-header { 
        text-align: center; 
        color: #1E3A5F; 
        font-size: 24px !important; /* 기존보다 축소 */
        font-weight: 800; 
        margin-top: 10px !important; 
        margin-bottom: 15px !important; 
        line-height: 1.2 !important; 
    }

    /* 검색 버튼 */
    div.stButton > button[kind="primary"] {
        background-color: #FF5252 !important; color: white !important;
        border-radius: 8px !important; height: 45px !important; font-weight: bold !important;
    }

    /* 날짜 표시 박스 및 버튼 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px; 
        border-radius: 15px; border: 1px solid #E1E8F0; margin: 15px 0;
    }
    .res-main-title { font-size: 19px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 10px; }
    
    div[data-testid="stHorizontalBlock"] div.stButton > button {
        background-color: #A3D2F3 !important; border: none !important;
        color: white !important; font-size: 18px !important; font-weight: bold !important;
        border-radius: 4px !important; width: 100% !important; height: 40px !important;
    }
    .res-sub-title { font-size: 18px !important; font-weight: 700; color: #333; line-height: 40px; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* [2] 카드 내부 폰트 및 줄간격 수정 */
    .building-header { font-size: 18px !important; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 3px; margin-top: 20px; margin-bottom: 10px; }
    .section-title { font-size: 15px; font-weight: bold; color: #444; margin: 10px 0 5px 0; }
    
    .event-card { border: 1px solid #E8E8E8; border-left: 5px solid #1E3A5F; padding: 12px; border-radius: 8px; margin-bottom: 10px; background-color: white; position: relative; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    
    .status-badge { position: absolute; top: 12px; right: 12px; padding: 1px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }
    .status-y { background-color: #FFF2E6; color: #FF8C00; } 
    .status-w { background-color: #E6F2FF; color: #007AFF; }
    
    .place-name { font-size: 16px; font-weight: 800; color: #1E3A5F; margin-bottom: 4px; display: block; }
    .card-row { font-size: 14px; margin-bottom: 3px; display: flex; align-items: center; line-height: 1.3; }
    .time-text { font-weight: bold; color: #E63946; font-size: 15px; }

    /* 하단 정보 행 (날짜 폰트 축소 및 줄간격 조정) */
    .info-sub { 
        font-size: 11.5px !important; /* 날짜/부서 폰트 더 축소 */
        color: #777; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        margin-top: 8px; 
        border-top: 1px solid #F3F3F3; 
        padding-top: 6px; 
        line-height: 1.2 !important; 
    }
    
    .footer-spacer { height: 100px; }
    .top-floating {
        position: fixed; bottom: 25px; right: 20px; background-color: #1E3A5F;
        color: white !important; width: 45px; height: 45px; border-radius: 50%;
        text-align: center; line-height: 45px; font-weight: bold; z-index: 1000;
        text-decoration: none; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# 3. 메인 UI
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-header">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

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
        df = pd.DataFrame(res.json().get('res', []))
        if not df.empty:
            for c in ['statNm', 'mgDeptNm', 'allowDay', 'startDt', 'endDt']:
                if c not in df.columns: df[c] = ""
        return df
    except: return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    st.markdown('<div id="result-start"></div>', unsafe_allow_html=True)
    df_raw = get_data(st.session_state.target_date)
    
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    cols = st.columns([1, 4, 1])
    with cols[0]:
        if st.button("⬅️", key="prev"): change_date(-1); st.rerun()
    with cols[1]:
        st.markdown(f'<div style="text-align:center;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with cols[2]:
        if st.button("➡️", key="next"): change_date(1); st.rerun()
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
                for _, r in t_df.iterrows():
                    has_content = True
                    s_cls = "status-y" if r['statNm'] == "예약확정" else "status-w"
                    st.markdown(f"""
                    <div class="event-card"><span class="status-badge {s_cls}">{r['statNm']}</span>
                        <span class="place-name">📍 {r['placeNm']}</span>
                        <div class="card-row"><span class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</span></div>
                        <div class="card-row">📄 {r['eventNm']}</div>
                        <div class="info-sub"><span>🗓️ {r['startDt']}</span><span>👥 {r['mgDeptNm']}</span></div>
                    </div>""", unsafe_allow_html=True)

            # 기간 대관
            if show_period:
                p_df = bu_df[(bu_df['startDt'] != bu_df['endDt']) & (bu_df['allowDay'].str.contains(target_weekday, na=False))]
                for _, r in p_df.iterrows():
                    has_content = True
                    weekdays = get_weekday_names(r['allowDay'])
                    st.markdown(f"""
                    <div class="event-card"><span class="status-badge status-y">예약확정</span>
                        <span class="place-name">📍 {r['placeNm']}</span>
                        <div class="card-row"><span class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</span></div>
                        <div class="card-row">📄 {r['eventNm']}</div>
                        <div class="info-sub"><span>🗓️ {r['startDt']} ~ {r['endDt']} <b>{weekdays}</b></span><span>👥 {r['mgDeptNm']}</span></div>
                    </div>""", unsafe_allow_html=True)

        if not has_content:
            st.markdown('<div style="color:gray; padding:10px; font-size:13px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer-spacer"></div>', unsafe_allow_html=True)

st.markdown('<a href="#top-anchor" class="top-floating">TOP</a>', unsafe_allow_html=True)
