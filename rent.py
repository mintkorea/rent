import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

def move_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (카드 표출 방법 및 정렬 대폭 개선)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    
    /* 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 8px; }
    
    /* 화살표 버튼 */
    div.stButton > button {
        background: none !important; border: none !important; 
        font-size: 28px !important; color: #1E3A5F !important; padding: 0 !important;
    }
    
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }
    
    /* [개선] 카드 디자인 및 정렬 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; 
        padding: 15px; border-radius: 8px; margin-top: 12px;
        background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
    .place-name { font-size: 17px; font-weight: 800; color: #1E3A5F; flex: 1; }
    .status-badge { padding: 2px 10px; font-size: 12px; border-radius: 15px; font-weight: bold; margin-left: 10px; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    
    .time-row { font-size: 16px; font-weight: 700; color: #FF4B4B; margin-bottom: 6px; }
    .event-name { font-size: 14px; color: #444; line-height: 1.5; background: #f9f9f9; padding: 8px; border-radius: 4px; }
    .day-info { font-size: 12px; color: #666; margin-top: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. 입력 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.write("**📅 날짜 및 건물 선택**")
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
selected_bu = [b for b in ALL_BUILDINGS if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v6_{b}")]

# [개선] 대관 유형 선택
st.write("**🗓️ 대관 유형 선택**")
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관", value=True)
with c2: show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직 (요일 필터링 강화)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    try:
        res = requests.get(url, params={"mode": "getReservedData", "start": d, "end": d}, timeout=10)
        if res.status_code == 200:
            return pd.DataFrame(res.json().get('res', []))
    except: pass
    return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    df_raw = get_data(st.session_state.target_date.strftime('%Y-%m-%d'))
    d = st.session_state.target_date
    w_idx = d.weekday() # 0:월 ~ 6:일
    target_weekday = str(w_idx + 1) # 서버 요일값 (1:월 ~ 7:일)
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # 타이틀 박스
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 4, 1])
    with col_l: st.button("⬅", key="p", on_click=move_date, args=(-1,))
    with col_m: st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with col_r: st.button("➡", key="n", on_click=move_date, args=(1,))
    st.markdown('</div>', unsafe_allow_html=True)

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        found = False
        if not df_raw.empty:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            
            # 필터링 로직: 당일 대관 vs 기간 대관(요일 체크)
            for _, row in bu_df.iterrows():
                is_p = row['startDt'] != row['endDt']
                
                # 기간 대관일 경우 해당 요일('dow')에 포함되는지 확인
                is_correct_day = True
                if is_p and row.get('dow'):
                    is_correct_day = target_weekday in str(row['dow'])

                if is_correct_day:
                    if (not is_p and show_today) or (is_p and show_period):
                        found = True
                        s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                        # 요일 텍스트 변환 (1,2,3 -> 월,화,수)
                        dow_map = {"1":"월","2":"화","3":"수","4":"목","5":"금","6":"토","7":"일"}
                        dow_txt = ",".join([dow_map[i] for i in str(row.get('dow','')) if i in dow_map])
                        
                        st.markdown(f"""
                            <div class="event-card">
                                <div class="card-top">
                                    <div class="place-name">📍 {row['placeNm']}</div>
                                    <span class="status-badge {s_cls}">{row['status']}</span>
                                </div>
                                <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                                <div class="event-name">📄 {row['eventNm']}</div>
                                {f'<div class="day-info">🗓 반복 요일: {dow_txt}</div>' if is_p else ''}
                            </div>
                        """, unsafe_allow_html=True)
        
        if not found:
            st.markdown('<div style="color:#999; padding:10px;">대관 내역이 없습니다.</div>', unsafe_allow_html=True)
