import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo

# 1. 페이지 설정 및 시간대
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# --- [로직] 세션 및 URL 파라미터 관리 (날짜 변경 시 초기화 방지) ---
if 'target_date' not in st.session_state:
    st.session_state.target_date = today_kst()

# URL에서 날짜 정보 가져오기
url_params = st.query_params
if "d" in url_params:
    try:
        st.session_state.target_date = datetime.strptime(url_params["d"], "%Y-%m-%d").date()
    except: pass

ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]

# 2. CSS 스타일 (원본 카드 디자인 유지 + 개방지침 폰트 확대)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .stCheckbox { margin-top: -10px !important; margin-bottom: -5px !important; }
    .sat { color: #0000FF !important; }
    .sun { color: #FF0000 !important; }
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px 8px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; border-bottom: none; line-height: 1.2 !important;
    }
    .res-main-title { font-size: 20px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 4px; }
    .res-sub-title { font-size: 18px !important; font-weight: 700; color: #333; }
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
    .nav-item:last-child { border-right: none !important; }
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 15px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px 14px; border-radius: 5px; margin-bottom: 12px !important; background-color: #ffffff; line-height: 1.4 !important; }
    .bottom-info { font-size: 12px; color: #666; margin-top: 8px; display: flex; justify-content: space-between; border-top: 1px solid #f0f0f0; padding-top: 6px; }

    /* 개방 지침 폰트 확대 섹션 */
    .open-card { border: 2px dashed #2E5077; padding: 15px; border-radius: 10px; margin-bottom: 15px; background-color: #F8FAFF; }
    .open-bu-title { font-weight: 800; color: #2E5077; font-size: 19px !important; margin-bottom: 10px; border-bottom: 2px solid #D1D9E6; }
    .open-room-name { font-weight: bold; color: #333; font-size: 17px !important; margin-bottom: 3px; }
    .open-room-time { font-size: 16px !important; color: #FF4B4B; font-weight: bold; margin-bottom: 5px; }
    .open-room-note { font-size: 14px !important; color: #444; line-height: 1.4; background: #eee; padding: 5px 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 3. 입력부
with st.form("search_form"):
    selected_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
    st.markdown('**🏢 건물 선택**')
    
    current_selected = []
    cols = st.columns(2)
    # URL 기반 초기값 설정
    initial_bus = url_params.get_all("b") if "b" in url_params else ["성의회관", "의생명산업연구원"]
    
    for i, bu in enumerate(ALL_BU):
        with cols[i % 2]:
            if st.checkbox(bu, value=(bu in initial_bus), key=f"f_{bu}"):
                current_selected.append(bu)
    
    st.markdown('**🗓️ 대관 유형**')
    c1, c2 = st.columns(2)
    show_t = c1.checkbox("당일", value=True)
    show_p = c2.checkbox("기간", value=True)
    
    submit = st.form_submit_button("🔍 검색 및 지침 확인", use_container_width=True)
    if submit:
        st.session_state.target_date = selected_date
        # URL 파라미터 업데이트 (rerun 없이 처리하기 위해 딕셔너리 재구성)
        new_params = {"d": selected_date.strftime("%Y-%m-%d"), "b": current_selected}
        st.query_params.from_dict(new_params)

# 4. 데이터 로드 로직 (get_data 함수 등 생략 - 기존과 동일)
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return pd.DataFrame(res.json().get('res', [])) if res.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

# 5. 결과 출력
d = st.session_state.target_date
df_raw = get_data(d)
v_wd = d.isoweekday() 
is_weekend = v_wd in [6, 7]

# 네비게이션 (날짜 변경 시 건물 필터 유지)
current_bus = st.query_params.get_all("b") if "b" in st.query_params else ["성의회관", "의생명산업연구원"]
bu_q = "".join([f"&b={b}" for b in current_bus])
prev_url = f"./?d={(d - timedelta(1)).strftime('%Y-%m-%d')}{bu_q}"
next_url = f"./?d={(d + timedelta(1)).strftime('%Y-%m-%d')}{bu_q}"

w_idx = d.weekday()
w_str, w_class = ['월','화','수','목','금','토','일'][w_idx], ("sat" if w_idx == 5 else ("sun" if w_idx == 6 else ""))

st.markdown(f"""
<div class="date-display-box">
    <span class="res-main-title">성의교정 대관 현황</span>
    <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
</div>
<div class="nav-link-bar">
    <a href="{prev_url}" target="_self" class="nav-item">◀ Before</a>
    <a href="./?d={today_kst().strftime('%Y-%m-%d')}{bu_q}" target="_self" class="nav-item">Today</a>
    <a href="{next_url}" target="_self" class="nav-item">Next ▶</a>
</div>
""", unsafe_allow_html=True)

# 메인 대관 내역 출력
for bu in current_bus:
    st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
    has_content = False
    if not df_raw.empty:
        bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
        if not bu_df.empty:
            for _, row in bu_df.sort_values(by='startTime').iterrows():
                has_content = True
                st.markdown(f"""
                <div class="event-card">
                    <div style="font-size:16px; font-weight:bold; color:#1E3A5F; margin-bottom:4px;">📍 {row['placeNm']}</div>
                    <div style="color:#FF4B4B; font-weight:bold; font-size:15px; margin:4px 0;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                    <div style="font-size:14px; color:#333; font-weight:bold;">📄 {row['eventNm']}</div>
                    <div class="bottom-info"><span>👥 {row['mgDeptNm']}</span></div>
                </div>""", unsafe_allow_html=True)
    if not has_content:
        st.markdown('<div style="color:#999; text-align:center; padding:15px; border:1px dashed #eee; font-size:13px;">내역 없음</div>', unsafe_allow_html=True)

# --- 6. [지침 반영] 강의실 개방 요청 일람 ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="building-header">🔓 초회 순찰 개방 지침</div>', unsafe_allow_html=True)

is_p_4th = (date(d.year, 3, 2) <= d <= date(d.year, 4, 30))
is_p_801 = (date(d.year, 2, 7) <= d <= date(d.year, 4, 24))

# 성의회관 섹션
sh_list = []
if not is_weekend:
    sh_list.append({"r": "421, 422, 521, 522호", "t": "주중: 오전 개방 / 오후 원칙적 폐쇄", "n": "학생 요청 시 무리한 퇴실 독촉 금지"})
    if is_p_4th:
        sh_list.append({"r": "402, 403, 404, 405, 406, 407호", "t": "08:00 ~ 20:00 (3/2~4/30)", "n": "첫 순찰 개방 / 마지막 순찰 잠금"})
    if v_wd == 2: sh_list.append({"r": "502-1호", "t": "19:00 ~ 22:00 (화)", "n": "대학원 박사과정 기간 개방"})
    elif v_wd == 3:
        sh_list.append({"r": "506호 (솔로몬)", "t": "15:00경 개방 (수)", "n": "매주 수요일 지침"})
        sh_list.append({"r": "502-1호", "t": "19:00 ~ 22:00 (수)", "n": "대학원 박사과정 기간 개방"})

if is_p_801:
    sh_note = "평일: START센터 직원 개방 / 야간 21:00 폐쇄만 수행" if not is_weekend else "주말: 학생 요청 시 해당 시간 동안만 개방"
    sh_list.append({"r": "801호", "t": "09:00 ~ 21:00 (2/7~4/24)", "n": sh_note})

if sh_list:
    sh_html = "".join([f'<div style="margin-bottom:12px;"><div class="open-room-name">• {i["r"]}</div><div class="open-room-time">⏰ {i["t"]}</div><div class="open-room-note">{i["n"]}</div></div>' for i in sh_list])
    st.markdown(f'<div class="open-card"><div class="open-bu-title">🏢 성의회관</div>{sh_html}</div>', unsafe_allow_html=True)

# 별관 섹션 (주말 포함 상시 노출)
bg_status = "월~금: 오전 개방 / 오후 폐쇄" if not is_weekend else "주말(토,일): 대관 현황 확인 후 개방"
bg_note = "1206호 매주 금요일 10시 교육 예정 (첫 순찰 개방 확인)" if v_wd == 5 else ("주말 지침에 따라 대관 확인 후 개방" if is_weekend else "평일 순찰 지침 준수")

st.markdown(f"""
<div class="open-card">
    <div class="open-bu-title">🏢 서울성모별관</div>
    <div class="open-room-name">• 1201, 1202, 1203, 1204, 1205, 1206호</div>
    <div class="open-room-time">⏰ {bg_status}</div>
    <div class="open-room-note">{bg_note}</div>
</div>
<div id="result-anchor"></div>
""", unsafe_allow_html=True)

if submit:
    components.html("<script>window.parent.document.getElementById('result-anchor').scrollIntoView();</script>", height=0)

st.markdown("""<div style="position:fixed; bottom:25px; right:20px; z-index:999;"><a href="#top-anchor" style="display:block; background:#1E3A5F; color:white !important; width:45px; height:45px; line-height:45px; text-align:center; border-radius:50%; font-size:12px; font-weight:bold; text-decoration:none !important; box-shadow:2px 4px 8px rgba(0,0,0,0.3);">TOP</a></div>""", unsafe_allow_html=True)
