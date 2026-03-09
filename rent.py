import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, date, timedelta

# 1. 페이지 설정 및 세션 관리
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

def move_date(days):
    st.session_state.target_date += timedelta(days=days)
    st.session_state.search_performed = True

# 2. CSS 스타일 (사용자님의 최신 카드 디자인 및 폰트 크기 완벽 반영)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    .main-title { font-size: 26px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px; }
    
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; padding: 20px 10px; 
        border-radius: 12px; margin-bottom: 20px; border: 1px solid #D1D9E6; 
    }
    .res-main-title { font-size: 24px !important; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 8px; }
    
    div.stButton > button { background: none !important; border: none !important; font-size: 30px !important; color: #1E3A5F !important; padding: 0 !important; }
    .res-sub-title { font-size: 21px !important; font-weight: 800; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* [최종] 카드 표출 방법 최적화 (Screenshot_162154 기준) */
    .building-header { font-size: 20px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 8px solid #2E5077; 
        padding: 15px; border-radius: 5px; margin-bottom: 12px;
        background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        position: relative;
    }
    .status-badge { position: absolute; top: 15px; left: 12px; font-size: 14px; font-weight: bold; color: #555; }
    .place-name { font-size: 19px; font-weight: 800; color: #1E3A5F; margin-left: 25px; margin-bottom: 8px; }
    .time-row { font-size: 17px; font-weight: 700; color: #FF4B4B; margin-left: 25px; margin-bottom: 10px; }
    .event-name { font-size: 15px; color: #444; line-height: 1.5; margin-left: 25px; border-top: 1px solid #f0f0f0; padding-top: 10px; }
    .dow-label { font-size: 13px; color: #007BFF; font-weight: bold; margin-left: 25px; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# 3. 사용자 입력 영역
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
c_bu = st.columns(2)
selected_bu = [b for i, b in enumerate(ALL_BUILDINGS) if c_bu[i%2].checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"f_bu_{b}")]

st.write("**🗓️ 대관 유형 선택**")
ct1, ct2 = st.columns(2)
with ct1: show_today = st.checkbox("당일 대관", value=True)
with ct2: show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 추출 로직 (추출 안 됨 문제 해결을 위한 재시도 로직)
def get_data_with_retry(d_str, retries=2):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": d_str, "end": d_str}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Whale/3.24.223.18'}
    
    for i in range(retries):
        try:
            res = requests.get(url, params=params, headers=headers, timeout=8)
            if res.status_code == 200 and res.text.strip().startswith('{'):
                return pd.DataFrame(res.json().get('res', []))
        except:
            time.sleep(1) # 지연 발생 시 1초 대기 후 재시도
    return pd.DataFrame()

# 5. 결과 필터링 및 카드 표출
if st.session_state.search_performed:
    d = st.session_state.target_date
    df_raw = get_data_with_retry(d.strftime('%Y-%m-%d'))
    
    w_idx = d.weekday() # 0(월)~6(일)
    cur_dow_str = str(w_idx + 1) # 서버 기준 1(월)~7(일)
    w_name = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_css = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # 타이틀 박스
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    cl, cm, cr = st.columns([1, 4, 1])
    with cl: st.button("⬅", key="p_v8", on_click=move_date, args=(-1,))
    with cm: st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_css}">({w_name})</span></span></div>', unsafe_allow_html=True)
    with cr: st.button("➡", key="n_v8", on_click=move_date, args=(1,))
    st.markdown('</div>', unsafe_allow_html=True)

    if df_raw.empty:
        st.warning(f"📍 {d.strftime('%Y-%m-%d')} 데이터 로딩에 실패했거나 대관 내역이 없습니다.")
    else:
        for bu in selected_bu:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            
            match_found = False
            for _, row in bu_df.iterrows():
                is_p = row['startDt'] != row['endDt']
                
                # [개선] 요일 필터링: 기간 대관인 경우 해당 요일이 포함되어야만 추출
                row_dow = str(row.get('dow', ''))
                is_on_day = cur_dow_str in row_dow if is_p else True

                if (not is_p and show_today) or (is_p and show_period and is_on_day):
                    match_found = True
                    d_map = {"1":"월","2":"화","3":"수","4":"목","5":"금","6":"토","7":"일"}
                    d_list = [d_map[i] for i in row_dow if i in d_map]
                    
                    st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge">{row['status']}</span>
                            <div class="place-name">📍 {row['placeNm']}</div>
                            <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                            {f'<div class="dow-label">🗓 반복 요일: {",".join(d_list)}</div>' if is_p else ''}
                        </div>
                    """, unsafe_allow_html=True)
            
            if not match_found:
                st.write("<div style='color:#888; padding-left:5px;'>조건에 맞는 대관 내역이 없습니다.</div>", unsafe_allow_html=True)
