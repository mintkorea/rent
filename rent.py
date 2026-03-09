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

# 2. CSS 스타일 (사용자님의 최신 카드 디자인 및 정렬 방식 적용)
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
    
    div.stButton > button {
        background: none !important; border: none !important; 
        font-size: 28px !important; color: #1E3A5F !important; padding: 0 !important;
    }
    .res-sub-title { font-size: 20px !important; font-weight: 700; color: #333; }
    .sat { color: #0000FF !important; } .sun { color: #FF0000 !important; }

    /* [최종] 카드 표출 및 정렬 디자인 */
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 25px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; 
        padding: 15px; border-radius: 8px; margin-bottom: 12px;
        background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        position: relative;
    }
    .status-badge { position: absolute; top: 15px; left: 15px; font-size: 14px; font-weight: bold; color: #555; }
    .place-name { font-size: 18px; font-weight: 800; color: #1E3A5F; margin-left: 25px; margin-bottom: 5px; }
    .time-row { font-size: 16px; font-weight: 700; color: #FF4B4B; margin-left: 25px; margin-bottom: 8px; }
    .event-name { font-size: 14px; color: #444; line-height: 1.5; margin-left: 25px; border-top: 1px solid #eee; padding-top: 8px; }
    .dow-info { font-size: 12px; color: #888; margin-left: 25px; margin-top: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. 입력부
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
st.session_state.target_date = st.date_input("날짜", value=st.session_state.target_date, label_visibility="collapsed")

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "대학본관", "서울성모별관"]
cols_bu = st.columns(2)
selected_bu = []
for i, b in enumerate(ALL_BUILDINGS):
    if cols_bu[i%2].checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v7_{b}"):
        selected_bu.append(b)

st.write("**🗓️ 대관 유형 선택**")
c_t1, c_t2 = st.columns(2)
with c_t1: show_today = st.checkbox("당일 대관", value=True)
with c_t2: show_period = st.checkbox("기간 대관", value=True)

if st.button("🔍 검색하기", use_container_width=True, type="primary"):
    st.session_state.search_performed = True

# 4. 데이터 로직 (추출 실패 방지 강화)
def get_data(d_str):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    try:
        # 학교 서버는 User-Agent가 없으면 차단할 수 있습니다.
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Whale/3.24.223.18'}
        res = requests.get(url, params={"mode": "getReservedData", "start": d_str, "end": d_str}, headers=headers, timeout=10)
        if res.status_code == 200:
            return pd.DataFrame(res.json().get('res', []))
    except: pass
    return pd.DataFrame()

# 5. 결과 출력
if st.session_state.search_performed:
    d = st.session_state.target_date
    df_raw = get_data(d.strftime('%Y-%m-%d'))
    
    w_idx = d.weekday() # 0(월)~6(일)
    server_dow = str(w_idx + 1) # 서버 기준 1(월)~7(일)
    w_str = ["월", "화", "수", "목", "금", "토", "일"][w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")

    # 타이틀 박스 (화살표 포함)
    st.markdown('<div class="date-display-box"><span class="res-main-title">성의교정 대관 현황</span>', unsafe_allow_html=True)
    cl, cm, cr = st.columns([1, 4, 1])
    with cl: st.button("⬅", key="prev", on_click=move_date, args=(-1,))
    with cm: st.markdown(f'<div style="margin-top:5px;"><span class="res-sub-title">{d.strftime("%Y.%m.%d")}.<span class="{w_class}">({w_str})</span></span></div>', unsafe_allow_html=True)
    with cr: st.button("➡", key="next", on_click=move_date, args=(1,))
    st.markdown('</div>', unsafe_allow_html=True)

    if df_raw.empty:
        st.info(f"📍 {d.strftime('%Y-%m-%d')} 대관 내역이 없습니다.")
    else:
        for bu in selected_bu:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)]
            
            found_count = 0
            for _, row in bu_df.iterrows():
                is_p = row['startDt'] != row['endDt'] # 기간 대관 여부
                
                # [핵심] 기간 대관 요일 매칭 검증
                is_target_day = True
                if is_p:
                    # dow 값이 "1,3,5" 처럼 쉼표로 오거나 "135" 처럼 올 때 모두 대응
                    row_dow = str(row.get('dow', ''))
                    is_target_day = server_dow in row_dow

                # 유형 필터링 적용
                if (not is_p and show_today) or (is_p and show_period and is_target_day):
                    found_count += 1
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    # 요일 텍스트 변환 (반복 요일 표시용)
                    d_map = {"1":"월","2":"화","3":"수","4":"목","5":"금","6":"토","7":"일"}
                    d_list = [d_map[i] for i in str(row.get('dow','')) if i in d_map]
                    d_text = ",".join(d_list)

                    st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge">{row['status']}</span>
                            <div class="place-name">📍 {row['placeNm']}</div>
                            <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                            {f'<div class="dow-info">🗓 반복: {d_text}</div>' if is_p else ''}
                        </div>
                    """, unsafe_allow_html=True)
            
            if found_count == 0:
                st.write("해당 조건의 대관 내역이 없습니다.")
