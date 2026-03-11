import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 1. 초기 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# --- [수정] 세션 및 URL 파라미터 우선 처리 ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# URL 파라미터 감지 (오늘/◀/▶ 클릭 시)
q = st.query_params
if "d" in q:
    try:
        url_d = datetime.strptime(q["d"], "%Y-%m-%d").date()
        st.session_state.target_date = url_d
        st.session_state.search_performed = True # 데이터 즉시 표시 강제
    except: pass

# 2. CSS 스타일 (image_e3ab7c 레이아웃 재현)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 네비게이션 링크 바 (검색 버튼 바로 아래 위치용) */
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 10px !important; 
        margin: 10px 0 !important; overflow: hidden !important;
    }
    .nav-link {
        flex: 1 !important; text-align: center !important; padding: 10px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important;
        font-weight: bold !important; border-right: 1px solid #F0F0F0 !important; font-size: 16px !important;
    }
    .nav-link:last-child { border-right: none !important; }
    
    /* 날짜 표시판 스타일 */
    .date-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px; 
        border-radius: 12px; border: 1px solid #D1D9E6; margin-top: 10px;
    }
    .res-title { font-size: 18px !important; font-weight: 800; color: #1E3A5F; border-bottom: 1px solid #D1D9E6; padding-bottom: 8px; margin-bottom: 10px; display: block; }
    .res-date { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 카드 스타일 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-top: 10px; background: white; }
</style>
""", unsafe_allow_html=True)

# 3. 메인 입력 UI
st.markdown('<h2 style="text-align:center;">🏫 성의교정 시설 대관 현황</h2>', unsafe_allow_html=True)

# 날짜 입력 및 건물 선택 (기본 UI)
curr_d = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
if curr_d != st.session_state.target_date:
    st.session_state.target_date = curr_d
    st.rerun()

st.markdown('**🏢 건물 선택**')
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_{b}")]

# [수정] 검색하기 버튼 위치 고정
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 결과 출력 (검색 이후에만 표시)
if st.session_state.search_performed:
    d = st.session_state.target_date
    
    # [위치 해결] 검색 버튼 바로 아래에 링크 바 배치
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

    # [위치 해결] 링크 바 아래에 날짜 박스 배치
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    st.markdown(f"""
        <div class="date-box">
            <span class="res-title">성의교정 대관 현황</span>
            <span class="res-date">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
        </div>
    """, unsafe_allow_html=True)

    # 데이터 로딩 및 카드 출력 (생략 없이 원본 로직 유지)
    @st.cache_data(ttl=300)
    def get_data(d_obj):
        url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
        params = {"mode": "getReservedData", "start": d_obj.strftime('%Y-%m-%d'), "end": d_obj.strftime('%Y-%m-%d')}
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))

    df = get_data(d)
    
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        if not df.empty:
            bu_df = df[df['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            if not bu_df.empty:
                for _, row in bu_df.sort_values(by='startTime').iterrows():
                    st.markdown(f"""<div class="event-card"><b>📍 {row['placeNm']}</b><br>⏰ {row['startTime']} ~ {row['endTime']}<br>📄 {row['eventNm']}</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#999; text-align:center; padding:10px;">내역 없음</div>', unsafe_allow_html=True)

# 5. 탑 버튼
st.markdown('<a href="#" style="position:fixed;bottom:25px;right:20px;width:45px;height:45px;background:#1E3A5F;color:white;border-radius:50%;text-align:center;line-height:45px;text-decoration:none;z-index:999;box-shadow:2px 4px 8px rgba(0,0,0,0.3);font-size:12px;font-weight:bold;">TOP</a>', unsafe_allow_html=True)
