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

# --- 세션 상태 및 URL 파라미터 동기화 (필터 유지 로직 추가) ---
url_params = st.query_params
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]

if 'target_date' not in st.session_state:
    if "d" in url_params:
        try: st.session_state.target_date = datetime.strptime(url_params["d"], "%Y-%m-%d").date()
        except: st.session_state.target_date = today_kst()
    else:
        st.session_state.target_date = today_kst()

if 'selected_bus' not in st.session_state:
    # URL에 b 파라미터가 있으면 복구, 없으면 기본값
    if "b" in url_params:
        st.session_state.selected_bus = url_params.get_all("b")
    else:
        st.session_state.selected_bus = ["성의회관", "의생명산업연구원"]

# 2. CSS 스타일 (폰트 대폭 확대 및 모바일 최적화)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    /* 전체 기본 폰트 크기 상향 */
    html, body, [class*="css"] { font-size: 16px !important; }
    
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .building-header { font-size: 22px !important; font-weight: bold; color: #2E5077; margin-top: 20px; border-bottom: 3px solid #2E5077; padding-bottom: 5px; margin-bottom: 15px; }
    
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px; 
        border-radius: 12px 12px 0 0; border: 1px solid #D1D9E6; line-height: 1.4 !important;
    }
    .res-main-title { font-size: 22px !important; font-weight: 800; color: #1E3A5F; display: block; }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    
    .nav-link-bar { display: flex; width: 100%; background: white; border: 1px solid #D1D9E6; border-radius: 0 0 10px 10px; margin-bottom: 25px; }
    .nav-item { flex: 1; text-align: center; padding: 12px 0; text-decoration: none !important; color: #1E3A5F !important; font-weight: bold; font-size: 16px; border-right: 1px solid #F0F0F0; }
    .nav-item:last-child { border-right: none; }

    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 15px; border-radius: 8px; margin-bottom: 15px !important; background-color: #ffffff; }
    .room-name { font-weight: bold; color: #333; font-size: 18px !important; }
    .room-time { font-size: 17px !important; color: #FF4B4B; font-weight: bold; margin-top: 5px; }
    .room-note { font-size: 15px !important; color: #555; line-height: 1.4; margin-top: 5px; background: #f2f2f2; padding: 5px 8px; border-radius: 4px; }
    
    .open-card { border: 2px dashed #2E5077; padding: 15px; border-radius: 10px; margin-bottom: 15px; background-color: #F8FAFF; }
    .open-bu-title { font-weight: 800; color: #2E5077; font-size: 18px !important; margin-bottom: 10px; border-bottom: 2px solid #D1D9E6; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 3. 입력부 (건물 선택 유지 로직)
with st.form("search_form"):
    selected_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
    st.markdown('**🏢 건물 선택**')
    
    current_selected = []
    cols = st.columns(2)
    for i, bu in enumerate(ALL_BU):
        with cols[i % 2]:
            if st.checkbox(bu, value=(bu in st.session_state.selected_bus), key=f"cb_{bu}"):
                current_selected.append(bu)
    
    submit = st.form_submit_button("🔍 검색 및 현장 개방지침 확인", use_container_width=True)
    if submit:
        st.session_state.target_date = selected_date
        st.session_state.selected_bus = current_selected
        st.session_state.search_performed = True
        # URL 파라미터 갱신
        new_params = {"d": selected_date.strftime("%Y-%m-%d")}
        for b in current_selected:
            if "b" not in new_params: new_params["b"] = []
            new_params["b"].append(b)
        st.query_params.update(**new_params)

# 4. 데이터 로드 (기존 동일)
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

# 네비게이션 링크 생성 (건물 필터 유지용)
bu_query = "".join([f"&b={b}" for b in st.session_state.selected_bus])
prev_url = f"./?d={(d - timedelta(1)).strftime('%Y-%m-%d')}{bu_query}"
next_url = f"./?d={(d + timedelta(1)).strftime('%Y-%m-%d')}{bu_query}"
today_url = f"./?d={today_kst().strftime('%Y-%m-%d')}{bu_query}"

w_idx = d.weekday()
w_str, w_class = ['월','화','수','목','금','토','일'][w_idx], ("sat" if w_idx == 5 else ("sun" if w_idx == 6 else ""))

st.markdown(f"""
<div class="date-display-box">
    <span class="res-main-title">성의교정 대관 현황</span>
    <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
</div>
<div class="nav-link-bar">
    <a href="{prev_url}" target="_self" class="nav-item">◀ Before</a>
    <a href="{today_url}" target="_self" class="nav-item">Today</a>
    <a href="{next_url}" target="_self" class="nav-item">Next ▶</a>
</div>
""", unsafe_allow_html=True)

# 대관 상세 내역 출력
for bu in st.session_state.selected_bus:
    st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
    has_content = False
    if not df_raw.empty:
        bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
        if not bu_df.empty:
            has_content = True
            for _, row in bu_df.sort_values(by='startTime').iterrows():
                st.markdown(f"""
                <div class="event-card">
                    <div class="room-name">📍 {row['placeNm']}</div>
                    <div class="room-time">⏰ {row['startTime']} ~ {row['endTime']}</div>
                    <div class="room-name" style="font-size:16px !important; color:#555;">📄 {row['eventNm']}</div>
                    <div style="font-size:14px; color:#888; margin-top:8px;">👥 {row['mgDeptNm']} | [ { "확정" if row['status']=='Y' else "대기" } ]</div>
                </div>""", unsafe_allow_html=True)
    if not has_content:
        st.markdown('<div style="color:#999; text-align:center; padding:20px; border:1px dashed #eee; font-size:16px;">대관 내역 없음</div>', unsafe_allow_html=True)

# --- 6. [지침 반영] 강의실 개방 요청 일람 (근무자 참조용) ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="building-header">🔓 초회 순찰 개방 지침</div>', unsafe_allow_html=True)

v_wd = d.isoweekday() 
is_weekend = v_wd in [6, 7]
is_p_4th = (date(d.year, 3, 2) <= d <= date(d.year, 4, 30))
is_p_801 = (date(d.year, 2, 7) <= d <= date(d.year, 4, 24))

# [1] 성의회관 지침 (주말엔 801호 외 노출 안됨)
sh_list = []
if not is_weekend:
    sh_list.append({"r": "421, 422, 521, 522호", "t": "주중: 오전 개방 / 오후 원칙적 폐쇄", "n": "학생 요청 시 무리한 퇴실 독촉 금지"})
    if is_p_4th:
        sh_list.append({"r": "402, 403, 404, 405, 406, 407호", "t": "08:00 ~ 20:00 (3/2~4/30)", "n": "첫 순찰 시 개방 / 마지막 순찰 시 잠금"})
    if v_wd == 2:
        sh_list.append({"r": "502-1호", "t": "19:00 ~ 22:00", "n": "대학원 박사과정 기간 개방 (화요일)"})
    elif v_wd == 3:
        sh_list.append({"r": "506호 (솔로몬의 방)", "t": "15:00경 개방", "n": "매주 수요일 개방 지침"})
        sh_list.append({"r": "502-1호", "t": "19:00 ~ 22:00", "n": "대학원 박사과정 기간 개방 (수요일)"})

# 801호는 주말에도 조건부 노출
if is_p_801:
    sh_note = "평일: START센터 직원 개방 / 야간 21시 폐쇄만 수행" if not is_weekend else "주말: 학생 요청 시 해당 시간 동안만 개방"
    sh_list.append({"r": "801호", "t": "09:00 ~ 21:00 (2/7~4/24)", "n": sh_note})

if sh_list:
    sh_html = "".join([f'<div class="room-item-box"><div class="room-name">• {i["r"]}</div><div class="room-time">⏰ {i["t"]}</div><div class="room-note">💡 {i["n"]}</div></div>' for i in sh_list])
    st.markdown(f'<div class="open-card"><div class="open-bu-title">🏢 성의회관</div>{sh_html}</div>', unsafe_allow_html=True)

# [2] 서울성모별관 지침 (주말 노출 포함)
bg_status = "평일: 오전 개방 / 오후 폐쇄" if not is_weekend else "주말: 대관 현황 확인 후 개방"
bg_note = "1206호 매주 금요일 10시 교육 예정 (첫 순찰 시 개방 확인)" if v_wd == 5 else ("주말 지침 적용" if is_weekend else "평일 순찰 지침 준수")

st.markdown(f"""
<div class="open-card">
    <div class="open-bu-title">🏢 서울성모별관</div>
    <div class="room-name">• 1201, 1202, 1203, 1204, 1205, 1206호</div>
    <div class="room-time">⏰ {bg_status}</div>
    <div class="room-note">💡 {bg_note}</div>
</div>
""", unsafe_allow_html=True)

# 하단 공백 및 TOP 버튼
st.write("")
st.write("")
st.markdown("""<div style="position:fixed; bottom:25px; right:20px; z-index:999;"><a href="#top-anchor" style="display:block; background:#1E3A5F; color:white !important; width:45px; height:45px; line-height:45px; text-align:center; border-radius:50%; font-size:12px; font-weight:bold; text-decoration:none !important; box-shadow:2px 4px 8px rgba(0,0,0,0.3);">TOP</a></div>""", unsafe_allow_html=True)
