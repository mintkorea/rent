import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

# 1. 한국 시간 및 공휴일 설정
KST = ZoneInfo("Asia/Seoul")
def today_kst(): return datetime.now(KST).date()

def is_holiday(d):
    holidays = [(1, 1), (3, 1), (5, 5), (6, 6), (8, 15), (10, 3), (10, 9), (12, 25)]
    return (d.month, d.day) in holidays

# 2. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state: st.session_state.target_date = today_kst()
if "search_performed" not in st.session_state: st.session_state.search_performed = False

# 3. [핵심] CSS 스타일 (색상 및 슬림 디자인 강제 주입)
st.markdown("""
<style>
    /* 전체 여백 조절 */
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    .main-title { font-size: 24px; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 10px; }
    .sub-label { font-size: 16px; font-weight: 800; color: #2E5077; margin-top: 5px; display: block; }

    /* 결과 박스 (최대한 얇고 깔끔하게) */
    .result-box-container {
        background-color: #F8FAFF;
        border: 1px solid #D1D9E6;
        border-radius: 12px;
        padding: 10px 8px;
        margin-top: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .result-title { font-size: 18px; font-weight: 800; color: #1E3A5F; text-align: center; margin-bottom: 8px; display: block; }
    
    /* 버튼 공통 스타일 */
    div[data-testid="stColumn"] button { 
        padding: 0px !important; 
        height: 40px !important;
        border-radius: 8px !important;
    }

    /* 요일별 색상 강제 (텍스트 클래스) */
    .blue-date p { color: #0047FF !important; font-weight: 800 !important; font-size: 16px !important; }
    .red-date p { color: #FF0000 !important; font-weight: 800 !important; font-size: 16px !important; }
    .black-date p { color: #333333 !important; font-weight: 800 !important; font-size: 16px !important; }

    /* 카드 디자인 */
    .building-header { font-size: 19px; font-weight: bold; color: #2E5077; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin: 15px 0 10px 0; }
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 12px; border-radius: 6px; margin-bottom: 10px; 
        background: white; line-height: 1.4 !important; 
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin-top: 3px; }
    .event-name { font-size: 14px; margin-top: 5px; color: #444; }

    .no-data-text { color: #888; font-size: 14px; padding: 15px; text-align: center; background: #f9f9f9; border: 1px dashed #ccc; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 4. 상단 입력부
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

c_bu, c_ty = st.columns(2)
with c_bu:
    st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
    ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    selected_bu = [b for b in ALL_BU if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"s_{b}")]
with c_ty:
    st.markdown('<span class="sub-label">🗓️ 유형 선택</span>', unsafe_allow_html=True)
    show_today = st.checkbox("당일 대관", value=True)
    show_period = st.checkbox("기간 대관", value=True)

st.write("")
if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 5. 데이터 함수
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 6. 결과 화면
if st.session_state.search_performed:
    # [박스 시작]
    st.markdown('<div class="result-box-container"><span class="result-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    
    # 내비게이션 행
    nc1, nc2, nc3 = st.columns([1, 4, 1])
    d = st.session_state.target_date
    w_idx = d.weekday()
    w_str = ['월','화','수','목','금','토','일'][w_idx]
    
    # 요일 색상 클래스 결정
    color_class = "black-date"
    if w_idx == 5: color_class = "blue-date"
    elif w_idx == 6 or is_holiday(d): color_class = "red-date"

    with nc1:
        if st.button("◀", key="p_nav", use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
    with nc2:
        # 중앙 버튼에 색상 클래스 적용된 컨테이너 사용
        st.markdown(f'<div class="{color_class}">', unsafe_allow_html=True)
        if st.button(f"{d.strftime('%Y.%m.%d')}.({w_str})", key="c_nav", use_container_width=True):
            st.session_state.target_date = today_kst()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with nc3:
        if st.button("▶", key="n_nav", use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 로드
    df_raw = get_data(d)
    target_weekday = str(w_idx + 1)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        has_bu = False
        
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ","").str.contains(bu.replace(" ",""), na=False)].copy()
            if not bu_df.empty:
                t_ev = bu_df[bu_df['startDt'] == bu_df['endDt']] if show_today else pd.DataFrame()
                p_ev = bu_df[bu_df['startDt'] != bu_df['endDt']] if show_period else pd.DataFrame()
                v_p_ev = p_ev[p_ev['allowDay'].apply(lambda x: target_weekday in [str(i).strip() for i in str(x).split(",")])] if not p_ev.empty else pd.DataFrame()

                # 통합 리스트 생성 (정렬용)
                combined = pd.concat([t_ev, v_p_ev]).sort_values(by='startTime')
                
                if not combined.empty:
                    has_bu = True
                    for _, row in combined.iterrows():
                        st.markdown(f"""
                        <div class="event-card">
                            <div class="place-name">📍 {row['placeNm']}</div>
                            <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)

        if not has_bu:
            st.markdown('<div class="no-data-text">대관 내역이 없습니다.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
