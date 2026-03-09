import streamlit as st  # 소문자 import 확인
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태 초기화 (에러 방지용)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# 2. CSS 스타일: 원본 기능 유지 + 줄간격 극소화 압축
st.markdown("""
<style>
    /* 전체 여백 조절 */
    .block-container { padding: 0.5rem 1rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* [핵심] 줄간격 및 요소 간격 압축 */
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div[data-testid="stCheckbox"] { margin-bottom: -15px !important; } /* 체크박스 간격 다닥다닥 */
    .stMarkdown p, .stMarkdown span, label { margin-bottom: 0px !important; line-height: 1.1 !important; font-size: 15px !important; }
    
    /* 제목 및 레이블 간격 축소 */
    .main-title { font-size: 22px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin: 5px 0 10px 0 !important; }
    .sub-label { font-size: 16px !important; font-weight: 800; color: #2E5077; margin-top: 8px !important; display: block; }

    /* 결과창 날짜 박스 (화살표 제거) */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 12px; 
        border-radius: 10px; margin: 10px 0; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 18px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 3px; }
    .res-sub-title { font-size: 17px !important; font-weight: 700; color: #333; }
    
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* 카드 디자인 압축 */
    .building-header { font-size: 17px !important; font-weight: bold; color: #2E5077; margin-top: 12px; border-bottom: 2px solid #2E5077; padding-bottom: 2px; margin-bottom: 6px; }
    .section-title { font-size: 14px; font-weight: bold; color: #555; margin: 6px 0 3px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 4px solid #2E5077; padding: 6px 10px; border-radius: 5px; margin-bottom: 5px !important; background-color: #ffffff; }
    .place-name { font-size: 14px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 13px; font-weight: bold; color: #FF4B4B; }
    .event-name { font-size: 13px; margin-top: 2px; color: #333; }
    .bottom-info { font-size: 10.5px; color: #666; margin-top: 3px; display: flex; justify-content: space-between; }
</style>
""", unsafe_allow_html=True)

# 3. 메인 UI (성공한 원본 항목 유지)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")
st.session_state.target_date = target_date

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"fixed_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_t_fixed")
show_period = st.checkbox("기간 대관", value=True, key="chk_p_fixed")

st.write(" ")
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직 (성공한 원본 그대로)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date)
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    
    # 상단 결과 박스 (화살표 제거)
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span>
    </div>
    """, unsafe_allow_html=True)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_content = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if not bu_df.empty:
                # 필터링
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                
                # 요일 체크
                tw = str(d.weekday() + 1)
                valid_p = p_ev[p_ev['allowDay'].apply(lambda x: tw in str(x).split(","))] if not p_ev.empty else pd.DataFrame()

                for title, target_ev in [("📌 당일 대관", t_ev), ("🗓️ 기간 대관", valid_p)]:
                    if not target_ev.empty:
                        has_content = True
                        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
                        for _, row in target_ev.sort_values(by='startTime').iterrows():
                            s_txt = "예약확정" if row['status'] == 'Y' else "신청대기"
                            st.markdown(f"""
                            
