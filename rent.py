import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 페이지 설정 및 시간대
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회(M)", page_icon="🏫", layout="centered")

# --- 내부 로직 ---
def get_weekday_names(codes):
    days = {"1":"월", "2":"화", "3":"수", "4":"목", "5":"금", "6":"토", "7":"일"}
    if not codes: return ""
    return ",".join([days.get(c.strip(), "") for c in str(codes).split(",") if c.strip() in days])

def get_work_shift(d):
    anchor = date(2026, 3, 13)
    diff = (d - anchor).days
    shifts = [{"n": "A조", "bg": "#FF9800"}, {"n": "B조", "bg": "#E91E63"}, {"n": "C조", "bg": "#2196F3"}]
    return shifts[diff % 3]

if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

url_params = st.query_params
if "d" in url_params:
    try:
        st.session_state.target_date = datetime.strptime(url_params["d"], "%Y-%m-%d").date()
        st.session_state.search_performed = True
    except: pass

# --- 🎨 CSS 스타일 (시간 강조 및 상태 간소화 디자인) ---
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    
    /* 날짜 헤더 영역 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none;
    }
    .res-sub-title { font-size: 19px !important; font-weight: 700; color: #333; }
    
    /* 네비게이션 바 */
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 0 0 10px 10px !important; 
        margin-bottom: 25px !important;
    }
    .nav-item {
        flex: 1 !important; text-align: center !important; padding: 12px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important; font-weight: bold !important; 
        border-right: 1px solid #F0F0F0 !important; font-size: 14px !important;
    }
    
    /* 카드 디자인 개선: 시간(Time) 강조 */
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin: 20px 0 10px 0; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 12px 14px; border-radius: 5px; margin-bottom: 12px !important; background-color: #ffffff; }
    
    /* 상단 행: 시간과 상태 */
    .card-top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
    .time-tag { font-size: 17px !important; font-weight: 800; color: #FF4B4B; }
    .status-mini { font-size: 12px; font-weight: bold; padding: 2px 8px; border-radius: 4px; }
    .st-confirm { background-color: #E8F5E9; color: #2E7D32; } /* 확정 */
    .st-waiting { background-color: #FFF3E0; color: #EF6C00; } /* 대기 */
    
    .place-name { font-size: 16px !important; font-weight: bold; color: #1E3A5F; margin-bottom: 4px; }
    .event-name { font-size: 14px !important; color: #333; line-height: 1.4; }
    .dept-name { font-size: 12px; color: #888; margin-top: 6px; border-top: 1px solid #f9f9f9; padding-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# --- 2. 검색 폼 ---
with st.form("search_form"):
    selected_date = st.date_input("날짜 선택", value=st.session_state.target_date, label_visibility="collapsed")
    st.markdown('**🏢 건물 선택**')
    ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    selected_bu_list = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_{b}")]
    if st.form_submit_button("🔍 검색", use_container_width=True):
        st.session_state.target_date = selected_date
        st.session_state.search_performed = True
        st.query_params["d"] = selected_date.strftime("%Y-%m-%d")
        st.rerun()

# --- 3. 데이터 로딩 ---
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return pd.DataFrame(res.json().get('res', [])) if res.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

# --- 4. 결과 출력 ---
if st.session_state.search_performed:
    d = st.session_state.target_date
    df_raw = get_data(d)
    shift = get_work_shift(d)
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]
    
    # 상단 정보바
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-sub-title">{d.strftime("%Y.%m.%d")} ({w_str})</span>
        <span style="background:{shift['bg']}; color:white; padding:2px 10px; border-radius:12px; font-size:14px; margin-left:5px;">근무 : {shift['n']}</span>
    </div>
    <div class="nav-link-bar">
        <a href="./?d={(d-timedelta(1)).strftime('%Y-%m-%d')}" target="_self" class="nav-item">◀ 이전</a>
        <a href="./?d={today_kst().strftime('%Y-%m-%d')}" target="_self" class="nav-item">오늘</a>
        <a href="./?d={(d+timedelta(1)).strftime('%Y-%m-%d')}" target="_self" class="nav-item">다음 ▶</a>
    </div>
    """, unsafe_allow_html=True)

    target_wd = str(d.weekday() + 1)
    for bu in selected_bu_list:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                # 당일/기간 통합 조회 (시간순 정렬)
                bu_df['is_p'] = bu_df['startDt'] != bu_df['endDt']
                display_df = bu_df[~bu_df['is_p'] | bu_df['allowDay'].apply(lambda x: target_wd in [day.strip() for day in str(x).split(",")])]
                
                if not display_df.empty:
                    has_content = True
                    for _, row in display_df.sort_values(by='startTime').iterrows():
                        # 상태 메시지 간소화
                        st_label, st_class = ("확정", "st-confirm") if row['status'] == 'Y' else ("대기", "st-waiting")
                        st.markdown(f"""
                        <div class="event-card">
                            <div class="card-top-row">
                                <span class="time-tag">⏰ {row['startTime']} ~ {row['endTime']}</span>
                                <span class="status-mini {st_class}">{st_label}</span>
                            </div>
                            <div class="place-name">📍 {row['placeNm']}</div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                            <div class="dept-name">👤 {row['mgDeptNm']} {"(기간)" if row['is_p'] else ""}</div>
                        </div>
                        """, unsafe_allow_html=True)
        if not has_content: st.markdown('<div style="color:#999; text-align:center; padding:10px; font-size:13px;">내역 없음</div>', unsafe_allow_html=True)

    # 5. 강의실 개방 지침 (생략 없이 유지)
    st.markdown("<br><div class=\"building-header\">🔓 강의실 개방 지침</div>", unsafe_allow_html=True)
    is_weekend = d.isoweekday() in [6, 7]
    if not is_weekend:
        st.info("💡 성의회관 421~522호: 오전 개방 / 오후 폐쇄 (요청 시 유연 대응)")
    else:
        st.warning("🔒 주말: 모든 강의실 폐쇄 원칙 (대관 시 해당 시간만 개방)")

    # 6. 링크 바
    with st.expander("🔗 관리 링크", expanded=False):
        st.markdown('<a href="https://todayshift.com/" target="_blank" style="text-decoration:none; color:#1E3A5F; font-weight:bold;">• 오늘근무 확인</a>', unsafe_allow_html=True)

    # 자동 스크롤 스크립트
    components.html("""<script>window.parent.document.querySelector('section.main').scrollTo(0, 0);</script>""", height=0)
