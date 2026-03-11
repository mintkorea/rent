import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 환경 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# --- [수정] URL 파라미터 처리 로직 (검색 상태 강제 유지) ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

q_params = st.query_params
if "d" in q_params:
    d_str = q_params["d"]
    try:
        url_date = datetime.strptime(d_str, "%Y-%m-%d").date()
        # URL에 날짜가 있으면 무조건 검색 결과 화면을 보여주도록 설정
        st.session_state.target_date = url_date
        st.session_state.search_performed = True 
    except: pass

# 2. CSS 스타일 (이미지 image_ee23a5 스타일 재현)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* Before Today Next 링크 바 (디자인 개선) */
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 10px !important; 
        margin: 10px 0 20px 0 !important; overflow: hidden !important;
    }
    .nav-link {
        flex: 1 !important; text-align: center !important; padding: 10px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important;
        font-weight: bold !important; border-right: 1px solid #F0F0F0 !important; font-size: 15px !important;
    }
    .nav-link:last-child { border-right: none !important; }
    .nav-link:hover { background-color: #F8FAFF !important; }

    /* 날짜 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 12px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 18px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; border-bottom: 1px solid #D1D9E6; padding-bottom: 5px; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 20px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background: white; line-height: 1.4; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 3. 입력부 (조회 설정)
target_date_input = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
# 달력으로 날짜 변경 시에도 검색 결과 유지
if target_date_input != st.session_state.target_date:
    st.session_state.target_date = target_date_input
    st.session_state.search_performed = True
    st.rerun()

st.markdown('**🏢 건물 선택**')
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}")]

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력
if st.session_state.search_performed:
    d = st.session_state.target_date
    
    # [위치 조정] Before / Today / Next 링크 바를 타이틀(날짜박스) 바로 위로 배치
    p_d = (d - timedelta(days=1)).strftime("%Y-%m-%d")
    n_d = (d + timedelta(days=1)).strftime("%Y-%m-%d")
    t_d = today_kst().strftime("%Y-%m-%d")
    st.markdown(f"""
        <div class="nav-link-bar">
            <a href="./?d={p_d}" target="_self" class="nav-link">◀</a>
            <a href="./?d={t_d}" target="_self" class="nav-link">오늘</a>
            <a href="./?d={n_d}" target="_self" class="nav-link">▶</a>
        </div>
    """, unsafe_allow_html=True)

    # 날짜 정보 박스
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    st.markdown(f'<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)

    # --- 데이터 로딩 및 출력 로직 (기존과 동일) ---
    @st.cache_data(ttl=300)
    def get_data(d_obj):
        url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
        params = {"mode": "getReservedData", "start": d_obj.strftime('%Y-%m-%d'), "end": d_obj.strftime('%Y-%m-%d')}
        try:
            res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
            return pd.DataFrame(res.json().get('res', []))
        except: return pd.DataFrame()

    df_raw = get_data(d)
    
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                has_content = True
                for _, row in bu_df.sort_values(by='startTime').iterrows():
                    s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                    st.markdown(f"""<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-name">📍 {row['placeNm']}</div><div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div><div class="event-name">📄 {row['eventNm']}</div></div>""", unsafe_allow_html=True)
        if not has_content:
            st.markdown('<div style="color:#999; text-align:center; padding:10px;">내역 없음</div>', unsafe_allow_html=True)

# 5. TOP 버튼
st.markdown('<a href="#top-anchor" style="position:fixed;bottom:25px;right:20px;width:45px;height:45px;background:#1E3A5F;color:white;border-radius:50%;text-align:center;line-height:45px;text-decoration:none;z-index:999;box-shadow:2px 4px 8px rgba(0,0,0,0.3);font-size:12px;font-weight:bold;">TOP</a>', unsafe_allow_html=True)
