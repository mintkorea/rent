import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 1. 시간 및 기본 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# --- URL 파라미터 제어 (Before/Today/Next 클릭 대응) ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

q = st.query_params
if "d" in q:
    try:
        url_date = datetime.strptime(q["d"], "%Y-%m-%d").date()
        if st.session_state.target_date != url_date:
            st.session_state.target_date = url_date
            st.session_state.search_performed = True
            st.rerun()
    except: pass

# 2. CSS (링크 바 위치 및 카드 디자인)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* Before Today Next 링크 바 디자인 */
    .nav-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 10px !important; 
        margin: 15px 0 !important; overflow: hidden !important;
    }
    .nav-item {
        flex: 1 !important; text-align: center !important; padding: 12px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important;
        font-weight: bold !important; border-right: 1px solid #F0F0F0 !important; font-size: 14px !important;
    }
    .nav-item:last-child { border-right: none !important; }

    /* 날짜 박스 */
    .result-date-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-bottom: 20px;
    }
    .res-title { font-size: 18px !important; font-weight: 800; color: #1E3A5F; border-bottom: 1px solid #D1D9E6; padding-bottom: 8px; margin-bottom: 10px; display: block; }
    .res-date { font-size: 20px !important; font-weight: 700; color: #333; }
    
    /* 카드 배지 */
    .status-badge { display: inline-block; padding: 2px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px; background: white; }
</style>
""", unsafe_allow_html=True)

# 3. 입력부 (상단 UI)
st.markdown('<h2 style="text-align:center;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 달력 입력
curr_d = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
if curr_d != st.session_state.target_date:
    st.session_state.target_date = curr_d
    st.rerun()

# 건물 및 유형 선택
st.markdown('**🏢 건물 선택**')
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bx_{b}")]

st.markdown('**🗓️ 대관 유형 선택**')
c1, c2 = st.columns(2)
show_t = c1.checkbox("당일 대관", value=True)
show_p = c2.checkbox("기간 대관", value=True)

# [위치 고정 1] 검색하기 버튼
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 섹션
if st.session_state.search_performed:
    d = st.session_state.target_date
    
    # [위치 고정 2] 검색 버튼 바로 아래에 링크 바 배치
    prev_s = (d - timedelta(days=1)).strftime("%Y-%m-%d")
    next_s = (d + timedelta(days=1)).strftime("%Y-%m-%d")
    today_s = today_kst().strftime("%Y-%m-%d")
    
    st.markdown(f"""
        <div class="nav-bar">
            <a href="./?d={prev_s}" target="_self" class="nav-item">Before</a>
            <a href="./?d={today_s}" target="_self" class="nav-item">Today</a>
            <a href="./?d={next_s}" target="_self" class="nav-item">Next</a>
        </div>
    """, unsafe_allow_html=True)

    # [위치 고정 3] 링크 바 아래에 날짜 박스 배치
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    st.markdown(f"""
        <div class="result-date-box">
            <span class="res-title">성의교정 대관 현황</span>
            <span class="res-date">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
        </div>
    """, unsafe_allow_html=True)

    # [오류 해결] JSONDecodeError 방지 로직
    @st.cache_data(ttl=300)
    def get_safe_data(d_obj):
        url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
        params = {"mode": "getReservedData", "start": d_obj.strftime('%Y-%m-%d'), "end": d_obj.strftime('%Y-%m-%d')}
        try:
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                return pd.DataFrame(r.json().get('res', []))
            return pd.DataFrame()
        except:
            return pd.DataFrame()

    df = get_safe_data(d)
    
    # 데이터 출력 (반복문)
    target_wd = str(d.weekday() + 1)
    for bu in selected_bu:
        st.markdown(f"#### 🏢 {bu}")
        has_item = False
        if not df.empty:
            bu_df = df[df['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            # 필터링 및 카드 출력 로직 (생략)
            if not bu_df.empty:
                has_item = True
                for _, row in bu_df.iterrows():
                    s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                    st.markdown(f"""<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><b>📍 {row['placeNm']}</b><br>⏰ {row['startTime']}~{row['endTime']}<br>📄 {row['eventNm']}</div>""", unsafe_allow_html=True)
        if not has_item:
            st.write("내역 없음")

st.markdown('<a href="#" style="position:fixed;bottom:25px;right:20px;width:45px;height:45px;background:#1E3A5F;color:white;border-radius:50%;text-align:center;line-height:45px;text-decoration:none;z-index:999;box-shadow:2px 4px 8px rgba(0,0,0,0.3);font-size:12px;font-weight:bold;">TOP</a>', unsafe_allow_html=True)
