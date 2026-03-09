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

# 2. CSS 스타일 (위아래 배치 방지 및 여백 제거)
st.markdown("""
<style>
    /* 전체 여백 극소화 */
    .block-container { padding: 0.2rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 텍스트 간격 조정 */
    p, div, label { margin-bottom: 0px !important; padding-bottom: 0px !important; line-height: 1.2 !important; }

    /* 메인 헤더 */
    .main-header { 
        text-align: center; color: #1E3A5F; font-size: 18px !important; 
        font-weight: 800; margin: 5px 0 !important; 
    }
    
    /* 날짜 이동 바 (한 줄 고정) */
    .date-nav-container {
        display: flex; align-items: center; justify-content: space-between;
        background-color: #F8FAFF; padding: 5px 10px; border-radius: 10px;
        border: 1px solid #E1E8F0; margin: 10px 0; height: 50px;
    }
    .res-sub-title { font-size: 16px !important; font-weight: 700; color: #333; flex-grow: 1; text-align: center; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* Streamlit 기본 버튼 스타일 강제 수정 (날짜이동용) */
    div[data-testid="column"] .stButton > button {
        background-color: #A3D2F3 !important; color: white !important;
        border: none !important; width: 40px !important; height: 35px !important;
        border-radius: 4px !important; font-size: 18px !important; font-weight: bold !important;
        padding: 0 !important; display: flex !important; align-items: center !important; justify-content: center !important;
    }

    /* 카드 디자인 (스크린샷 18:57 완벽 복제) */
    .building-header { font-size: 16px !important; font-weight: bold; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 2px; margin-top: 10px; margin-bottom: 5px; }
    .section-title { font-size: 13px; font-weight: bold; color: #444; margin: 8px 0 3px 0 !important; display: flex; align-items: center; }
    
    .event-card { 
        border: 1px solid #E8E8E8; border-left: 4px solid #1E3A5F; 
        padding: 8px 10px; border-radius: 6px; margin-bottom: 5px; 
        background-color: white; position: relative; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .status-badge { position: absolute; top: 8px; right: 8px; padding: 1px 6px; border-radius: 8px; font-size: 9px; font-weight: bold; }
    .status-y { background-color: #FFF2E6; color: #FF8C00; } 
    .status-w { background-color: #E6F2FF; color: #007AFF; }
    
    .place-name { font-size: 14px; font-weight: 800; color: #1E3A5F; margin-bottom: 2px; display: block; }
    .card-row { font-size: 13px; margin-bottom: 1px; display: flex; align-items: center; }
    .time-text { font-weight: bold; color: #E63946; font-size: 13.5px; }

    .info-sub { 
        font-size: 10.5px !important; color: #888; display: flex; 
        justify-content: space-between; align-items: center; 
        margin-top: 4px; border-top: 1px solid #F8F8F8; padding-top: 3px; 
    }
</style>
""", unsafe_allow_html=True)

# 3. 메인 UI
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-header">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 입력 영역 (최대한 좁게 배치)
st.markdown('<div class="section-title">📅 날짜 선택</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

st.markdown('<div class="section-title">🏢 건물 선택</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = []
for i, b in enumerate(ALL_BU):
    target_col = col1 if i % 2 == 0 else col2
    if target_col.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"sel_{b}"):
        selected_bu.append(b)

st.markdown('<div class="section-title">📋 대관 유형</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
show_today = c1.checkbox("당일 대관", value=True)
show_period = c2.checkbox("기간 대관", value=True)

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

    # [수정] 날짜 이동 바 - 위아래 배치를 방지하기 위해 columns 비율 고정 및 높이 정렬
    st.markdown('<div style="background-color:#F8FAFF; padding:5px 10px; border-radius:12px; border:1px solid #E1E8F0; margin:10px 0;">', unsafe_allow_html=True)
    cols = st.columns([1, 4, 1])
    with cols[0]:
        if st.button("⬅️", key="prev"): change_date(-1); st.rerun()
    with cols[1]:
        st.markdown(f'<div style="text-align:center; line-height:35px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with cols[2]:
        if st.button("➡️", key="next"): change_date(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    target_weekday = str(w_idx + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)]
            
            for mode, is_show in [("📌 당일 대관", show_today), ("📅 기간 대관", show_period)]:
                if is_show:
                    if mode == "📌 당일 대관":
                        sub_df = bu_df[bu_df['startDt'] == bu_df['endDt']]
                    else:
                        sub_df = bu_df[(bu_df['startDt'] != bu_df['endDt']) & (bu_df['allowDay'].str.contains(target_weekday, na=False))]
                    
                    if not sub_df.empty:
                        has_content = True
                        st.markdown(f'<div class="section-title">{mode}</div>', unsafe_allow_html=True)
                        for _, r in sub_df.iterrows():
                            s_cls = "status-y" if r['statNm'] == "예약확정" else "status-w"
                            repeat = get_weekday_names(r['allowDay']) if mode == "📅 기간 대관" else ""
                            st.markdown(f"""
                            <div class="event-card"><span class="status-badge {s_cls}">{r['statNm']}</span>
                                <span class="place-name">📍 {r['placeNm']}</span>
                                <div class="card-row"><span class="time-text">⏰ {r['startTime']} ~ {r['endTime']}</span></div>
                                <div class="card-row">📄 {r['eventNm']}</div>
                                <div class="info-sub"><span>🗓️ {r['startDt']}{" ~ "+r['endDt'] if repeat else ""} <b>{repeat}</b></span><span>👥 {r['mgDeptNm']}</span></div>
                            </div>""", unsafe_allow_html=True)

        if not has_content:
            st.markdown('<div style="color:gray; padding:2px; font-size:12px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

st.markdown('<a href="#top-anchor" style="position:fixed; bottom:20px; right:20px; background-color:#1E3A5F; color:white !important; width:40px; height:40px; border-radius:50%; text-align:center; line-height:40px; font-weight:bold; z-index:1000; text-decoration:none; font-size:10px; box-shadow:0 2px 5px rgba(0,0,0,0.2);">TOP</a>', unsafe_allow_html=True)
