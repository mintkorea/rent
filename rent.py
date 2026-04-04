import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 페이지 설정 및 시간대 (모바일 최적화)
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회(M)", page_icon="🏫", layout="centered")

# --- 🛠️ 핵심 로직 (인수인계 포인트) ---

def get_weekday_names(codes):
    """요일 코드(1,2,3)를 한글로 변환"""
    days = {"1":"월", "2":"화", "3":"수", "4":"목", "5":"금", "6":"토", "7":"일"}
    if not codes: return ""
    return ",".join([days.get(c.strip(), "") for c in str(codes).split(",") if c.strip() in days])

def get_work_shift(d):
    """근무조 자동 계산 (2026-03-13 기준)"""
    anchor = date(2026, 3, 13)
    diff = (d - anchor).days
    shifts = [{"n": "A조", "bg": "#FF9800"}, {"n": "B조", "bg": "#E91E63"}, {"n": "C조", "bg": "#2196F3"}]
    return shifts[diff % 3]

# 이동 및 검색 상태 유지
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# URL 파라미터 처리 (링크 공유용)
url_params = st.query_params
if "d" in url_params:
    try:
        st.session_state.target_date = datetime.strptime(url_params["d"], "%Y-%m-%d").date()
        st.session_state.search_performed = True
    except: pass

# --- 🎨 모바일 전용 CSS (기존 디자인 유지) ---
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px 8px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none;
    }
    .res-main-title { font-size: 20px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 4px; }
    .nav-link-bar {
        display: flex !important; width: 100% !important; background: white !important; 
        border: 1px solid #D1D9E6 !important; border-radius: 0 0 10px 10px !important; 
        margin-bottom: 25px !important; overflow: hidden !important;
    }
    .nav-item {
        flex: 1 !important; text-align: center !important; padding: 10px 0 !important;
        text-decoration: none !important; color: #1E3A5F !important; font-weight: bold !important; 
        border-right: 1px solid #F0F0F0 !important; font-size: 13px !important;
    }
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px 14px; border-radius: 5px; margin-bottom: 12px !important; background-color: #ffffff; }
    .status-badge { display: inline-block; padding: 2px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } .status-n { background-color: #E8F0FE; color: #1967D2; }
    .open-card { border: 2px dashed #2E5077; padding: 15px; border-radius: 10px; margin-bottom: 15px; background-color: #F8FAFF; }
    .link-btn { display: block; padding: 10px 0; color: #1E3A5F !important; text-decoration: none; font-weight: bold; font-size: 14px; border-bottom: 1px solid #eee; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 2. 입력부
with st.form("search_form"):
    selected_date = st.date_input("날짜 선택", value=st.session_state.target_date, label_visibility="collapsed")
    st.markdown('**🏢 건물 선택**')
    ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    # 건물 선택 최적화
    cols = st.columns(2)
    selected_bu_list = []
    for i, bu in enumerate(ALL_BU):
        if cols[i%2].checkbox(bu, value=(bu in ["성의회관", "의생명산업연구원"]), key=f"cb_{bu}"):
            selected_bu_list.append(bu)
            
    if st.form_submit_button("🔍 검색", use_container_width=True):
        st.session_state.target_date = selected_date
        st.session_state.search_performed = True
        st.query_params["d"] = selected_date.strftime("%Y-%m-%d")
        st.rerun()

# 3. 데이터 가져오기 (오류 방지 강화)
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = res.json().get('res', [])
        return pd.DataFrame(data) if data else pd.DataFrame()
    except: return pd.DataFrame()

# 4. 결과 출력
if st.session_state.search_performed:
    st.markdown('<div id="result-anchor"></div>', unsafe_allow_html=True)
    d = st.session_state.target_date
    df_raw = get_data(d)
    shift = get_work_shift(d)
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    
    # 상단 날짜 및 근무조 바
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">{d.strftime("%Y.%m.%d")} ({w_str})</span>
        <span style="background:{shift['bg']}; color:white; padding:3px 12px; border-radius:12px; font-size:14px; font-weight:bold;">근무 : {shift['n']}</span>
    </div>
    <div class="nav-link-bar">
        <a href="./?d={(d-timedelta(1)).strftime('%Y-%m-%d')}" target="_self" class="nav-item">◀ 이전</a>
        <a href="./?d={today_kst().strftime('%Y-%m-%d')}" target="_self" class="nav-item">오늘</a>
        <a href="./?d={(d+timedelta(1)).strftime('%Y-%m-%d')}" target="_self" class="nav-item">다음 ▶</a>
    </div>
    """, unsafe_allow_html=True)

    # 건물별 대관 내역
    target_wd = str(d.weekday() + 1)
    for bu in selected_bu_list:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                # 당일/기간 분류 로직
                for is_p, title in [(False, "📌 당일 대관"), (True, "🗓️ 기간 대관")]:
                    ev_df = bu_df[(bu_df['startDt'] != bu_df['endDt']) == is_p]
                    if is_p: # 기간 대관은 요일 체크 추가
                        ev_df = ev_df[ev_df['allowDay'].apply(lambda x: target_wd in [day.strip() for day in str(x).split(",")])]
                    
                    if not ev_df.empty:
                        has_content = True
                        st.markdown(f'<div style="font-size:14px; font-weight:bold; color:#666; margin-bottom:8px;">{title}</div>', unsafe_allow_html=True)
                        for _, row in ev_df.sort_values(by='startTime').iterrows():
                            s_cls, s_txt = ("status-y", "확정") if row['status'] == 'Y' else ("status-n", "대기")
                            st.markdown(f"""
                            <div class="event-card">
                                <span class="status-badge {s_cls}">{s_txt}</span>
                                <div style="font-size:16px; font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']}</div>
                                <div style="color:#FF4B4B; font-weight:bold; margin:4px 0;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                                <div style="font-size:14px; color:#333;"><b>📄 {row['eventNm']}</b></div>
                                <div style="font-size:12px; color:#888; margin-top:5px;">👤 {row['mgDeptNm']} ({row['peopleCount']}명)</div>
                            </div>
                            """, unsafe_allow_html=True)
        if not has_content: st.markdown('<div style="color:#999; text-align:center; padding:10px; font-size:13px;">대관 내역 없음</div>', unsafe_allow_html=True)

    # 5. 강의실 개방 지침 (기존 로직 유지)
    st.markdown("<br><div class=\"building-header\">🔓 강의실 개방 지침</div>", unsafe_allow_html=True)
    is_weekend = d.isoweekday() in [6, 7]
    open_list = []
    if not is_weekend:
        open_list.append({"r": "421, 422, 521, 522호", "t": "주중: 오전 개방 / 오후 폐쇄", "n": "학생 요청 시 유연하게 대응"})
    
    if open_list:
        sh_html = "".join([f'<div style="margin-bottom:10px;"><div style="font-weight:bold;">• {i["r"]}</div><div style="color:#FF4B4B; font-size:14px;">{i["t"]}</div><div style="font-size:13px; color:#666;">{i["n"]}</div></div>' for i in open_list])
        st.markdown(f'<div class="open-card"><div style="font-weight:800; color:#2E5077; border-bottom:1px solid #D1D9E6; margin-bottom:8px;">🏢 성의회관</div>{sh_html}</div>', unsafe_allow_html=True)

    # 6. 자주 찾는 링크
    with st.expander("🔗 주요 관리 링크", expanded=False):
        st.markdown('''
            <a href="https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do" target="_blank" class="link-btn">• 대관신청 현황(공식)</a>
            <a href="https://todayshift.com/" target="_blank" class="link-btn">• 오늘근무 확인</a>
            <a href="https://www.onsafe.co.kr" target="_blank" class="link-btn">• 법정교육(온세이프)</a>
        ''', unsafe_allow_html=True)

    components.html("""<script>setTimeout(function() {window.parent.document.getElementById('result-anchor').scrollIntoView({behavior: 'smooth', block: 'start'});}, 300);</script>""", height=0)
