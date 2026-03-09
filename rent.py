import streamlit as st  # 소문자 import로 수정
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# [개선] CSS 스타일: 원본 기능 유지 + 줄간격 극소화
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 0.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* [핵심] 모든 요소의 상하 간격 줄이기 */
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div[data-testid="stCheckbox"] { margin-bottom: -15px !important; } /* 체크박스 간격 압축 */
    .stMarkdown p, .stMarkdown span { margin-bottom: 0px !important; line-height: 1.2 !important; }
    
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 10px !important; }
    .sub-label { font-size: 16px !important; font-weight: 800; color: #2E5077; margin-top: 10px !important; display: block; }

    /* 결과 출력 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 15px 10px; 
        border-radius: 12px; margin: 10px 0; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 20px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 5px; }
    .res-sub-title { font-size: 18px !important; font-weight: 700; color: #333; }
    
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 12px; border-bottom: 2px solid #2E5077; padding-bottom: 3px; margin-bottom: 8px; }
    .section-title { font-size: 15px; font-weight: bold; color: #555; margin: 8px 0 4px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    
    /* 카드 디자인 압축 */
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 6px 10px; border-radius: 5px; margin-bottom: 6px !important; background-color: #ffffff; }
    .place-name { font-size: 15px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 14px; font-weight: bold; color: #FF4B4B; }
    .event-name { font-size: 13.5px; margin-top: 2px; color: #333; }
    .bottom-info { font-size: 11px; color: #666; margin-top: 4px; display: flex; justify-content: space-between; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 메인 UI (원본 리스트 유지)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v49_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_today_49")
show_period = st.checkbox("기간 대관", value=True, key="chk_period_49")

st.write(" ")
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 3. 데이터 로직 (원본 동일)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_str = ['월','화','수','목','금','토','일'][d.weekday()]
    w_class = "sat" if d.weekday() == 5 else ("sun" if d.weekday() == 6 else "")
    
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
    </div>
    """, unsafe_allow_html=True)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_bu_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                # 당일/기간 필터링
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                
                # 요일 필터 (기간 대관용)
                target_w = str(d.weekday() + 1)
                valid_period = period_ev[period_ev['allowDay'].apply(lambda x: target_w in str(x).split(","))] if not period_ev.empty else pd.DataFrame()
                
                # 출력 로직
                for title, target_ev, is_today in [("📌 당일 대관", today_ev, True), ("🗓️ 기간 대관", valid_period, False)]:
                    if not target_ev.empty:
                        has_bu_content = True
                        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
                        for _, row in target_ev.sort_values(by='startTime').iterrows():
                            s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                            s_txt = "예약확정" if row['status'] == 'Y' else "신청대기"
                            st.markdown(f"""
                            <div class="event-card">
                                <span class="status-badge {s_cls}" style="float:right; font-size:10px; padding:1px 5px; border-radius:10px;">{s_txt}</span>
                                <div class="place-name">📍 {row['placeNm']}</div>
                                <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                                <div class="event-name">📄 {row['eventNm']}</div>
                                <div class="bottom-info"><span>🗓️ {row['startDt']}</span><span>👥 {row['mgDeptNm']}</span></div>
                            </div>""", unsafe_allow_html=True)

        if not has_bu_content:
            st.markdown('<div style="color:#888; font-size:13px; padding-left:5px;">대관 내역이 없습니다.</div>', unsafe_allow_html
