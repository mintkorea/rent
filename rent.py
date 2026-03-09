import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태 초기화 (날짜 이동 및 건물 유지용)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()

# CSS 스타일
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 타이틀 및 날짜 컨트롤러 UI (이미지 스타일 구현) */
    .date-controller-container {
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(to bottom, #ffffff 0%, #f0f0f0 100%);
        border: 1px solid #ccc;
        border-radius: 50px;
        padding: 5px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .date-display-center {
        flex: 1;
        background: white;
        margin: 0 5px;
        border-radius: 10px;
        border: 1px solid #ddd;
        text-align: center;
        padding: 8px 0;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .res-main-title { font-size: 16px; font-weight: 800; color: #1E3A5F; display: block; line-height: 1.2; }
    .res-sub-title { font-size: 14px; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 기존 스타일 유지 */
    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 5px !important; display: block; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 8px 12px; border-radius: 5px; margin-bottom: 10px !important; background-color: #ffffff; line-height: 1.2 !important; }
    .today-card { background-color: #F8FAFF; } 
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; }
    .top-link-container { position: fixed; bottom: 25px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 45px; height: 45px; line-height: 45px; text-align: center; border-radius: 50%; font-size: 12px; font-weight: bold; text-decoration: none !important; }
    .no-data-text { color: #888; font-size: 14px; padding: 10px 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date # 세션 갱신

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_today")
show_period = st.checkbox("기간 대관", value=True, key="chk_period")

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

def get_weekday_names(allow_day_str):
    days = {"1":"월", "2":"화", "3":"수", "4":"목", "5":"금", "6":"토", "7":"일"}
    if not allow_day_str: return ""
    day_list = [days.get(d.strip()) for d in str(allow_day_str).split(",") if days.get(d.strip())]
    return f"({','.join(day_list)})"

# 4. 결과 출력 및 날짜 이동 컨트롤러
if search_clicked or 'auto_search' in st.session_state:
    if 'auto_search' in st.session_state: del st.session_state.auto_search

    # 날짜 요일 계산
    weekday_dict = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금', 5: '토', 6: '일'}
    w_idx = st.session_state.target_date.weekday()
    w_str = weekday_dict[w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    formatted_date = st.session_state.target_date.strftime("%Y.%m.%d")

    # 이미지 스타일 날짜 컨트롤러 레이아웃
    col_prev, col_mid, col_next = st.columns([1, 4, 1])
    
    with col_prev:
        if st.button(" < ", key="prev_day", use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.session_state.auto_search = True
            st.rerun()
            
    with col_mid:
        st.markdown(f"""
        <div class="date-controller-container">
            <div class="date-display-center">
                <span class="res-main-title">성의교정 대관 현황</span>
                <span class="res-sub-title">{formatted_date}.<span class="{w_class}">({w_str})</span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_next:
        if st.button(" > ", key="next_day", use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.session_state.auto_search = True
            st.rerun()

    # 데이터 조회
    df_raw = get_data(st.session_state.target_date)
    target_weekday = str(st.session_state.target_date.weekday() + 1)

    # 결과 출력 (건물별 개별 체크)
    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_bu_content = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                valid_period_ev = period_ev[period_ev['allowDay'].apply(lambda x: target_weekday in [d.strip() for d in str(x).split(",")])] if not period_ev.empty else pd.DataFrame()
                
                if not today_ev.empty:
                    has_bu_content = True
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in today_ev.sort_values(by='startTime').iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f'<div class="event-card today-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-name">📍 {row["placeNm"]}</div><div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div class="event-name">📄 {row["eventNm"]}</div><div class="bottom-info"><span class="period-label">🗓️ {row["startDt"]}</span><span class="dept-label">👥 {row["mgDeptNm"]}</span></div></div>', unsafe_allow_html=True)
                
                if not valid_period_ev.empty:
                    has_bu_content = True
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in valid_period_ev.sort_values(by='startTime').iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        day_info = get_weekday_names(row['allowDay'])
                        st.markdown(f'<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-name">📍 {row["placeNm"]}</div><div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div><div class="event-name">📄 {row["eventNm"]}</div><div class="bottom-info"><span class="period-label">🗓️ {row["startDt"]} ~ {row["endDt"]} <span style="color:#2E5077;">{day_info}</span></span><span class="dept-label">👥 {row["mgDeptNm"]}</span></div></div>', unsafe_allow_html=True)

        if not has_bu_content:
            st.markdown('<div class="no-data-text">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    # 하단 여백 및 TOP 버튼
    st.markdown('<div style="margin-bottom: 100px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
