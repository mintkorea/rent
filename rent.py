import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 1. 시간 및 세션 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# URL 파라미터 감지 (링크 클릭 시 동작)
q = st.query_params
if "d" in q:
    try:
        url_d = datetime.strptime(q["d"], "%Y-%m-%d").date()
        if st.session_state.target_date != url_d:
            st.session_state.target_date = url_d
            st.session_state.search_performed = True
            st.rerun()
    except: pass

# 2. CSS 스타일 (원본 디자인 및 링크 바)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    /* 날짜 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none;
    }
    /* [수정] 링크 바 스타일 - 타이틀 박스 바로 아래 붙도록 설정 */
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 0 0 10px 10px !important; 
        margin-bottom: 20px !important; overflow: hidden !important;
    }
    .nav-item {
        flex: 1 !important; text-align: center !important; padding: 10px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important;
        font-weight: bold !important; border-right: 1px solid #F0F0F0 !important; font-size: 14px !important;
    }
    .nav-item:last-child { border-right: none !important; }
    
    .res-main-title { font-size: 18px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 20px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-top: 10px; background: white; }
    .status-badge { display: inline-block; padding: 2px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)

# 3. 조회 설정 UI
t_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
if t_date != st.session_state.target_date:
    st.session_state.target_date = t_date
    st.rerun()

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v_{b}")]

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 섹션
if st.session_state.search_performed:
    d = st.session_state.target_date
    
    # [위치 수정] 1. 먼저 날짜 박스 출력
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.({w_str})</span>
    </div>
    """, unsafe_allow_html=True)

    # [위치 수정] 2. 박스 바로 아래에 링크 바 출력
    p_s, t_s, n_s = (d-timedelta(1)).isoformat(), today_kst().isoformat(), (d+timedelta(1)).isoformat()
    st.markdown(f"""
    <div class="nav-link-bar">
        <a href="./?d={p_s}" target="_self" class="nav-item">Before</a>
        <a href="./?d={t_s}" target="_self" class="nav-item">Today</a>
        <a href="./?d={n_s}" target="_self" class="nav-item">Next</a>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 가져오기 (JSON 에러 방지 포함)
    @st.cache_data(ttl=300)
    def get_data(d_obj):
        url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
        params = {"mode": "getReservedData", "start": d_obj.isoformat(), "end": d_obj.isoformat()}
        try:
            r = requests.get(url, params=params, timeout=10)
            return pd.DataFrame(r.json().get('res', []))
        except: return pd.DataFrame()

    df = get_data(d)
    
    # 건물별 데이터 출력
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_data = False
        if not df.empty:
            # 공백 제거 후 비교하여 정확도 높임
            bu_df = df[df['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            if not bu_df.empty:
                has_data = True
                for _, row in bu_df.sort_values(by='startTime').iterrows():
                    s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div style="font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']}</div>
                        <div style="color:#FF4B4B; font-weight:bold;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div style="margin-top:5px;">📄 {row['eventNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        if not has_data:
            st.markdown('<div style="color:#999; text-align:center; padding:15px;">내역 없음</div>', unsafe_allow_html=True)
