import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 상태로 날짜 관리 (버튼 클릭 시 유지 목적)
if 'target_date' not in st.session_state:
    st.session_state.target_date = date(2026, 3, 12)

# 요일 및 근무조 설정
WEEKDAY_KR = ['월', '화', '수', '목', '금', '토', '일']
SHIFT_TYPES = ['A조', 'B조', 'C조']
WEEKDAY_MAP = {"1": "월", "2": "화", "3": "수", "4": "목", "5": "금", "6": "토", "7": "일"}

def get_shift_group(dt):
    """2026년 1월 1일(B조) 기준 3교대 순환"""
    base_date = date(2026, 1, 1)
    diff = (dt - base_date).days
    return SHIFT_TYPES[(diff + 1) % 3]

# CSS: image_82e95c.jpg의 카드 스타일과 버튼 레이아웃 적용
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 16px !important; font-weight: 800; color: #2E5077; margin-top: 10px !important; display: block; }
    
    /* 날짜 표시 박스 스타일 */
    .header-box {
        background-color: #F0F2F6; padding: 10px; border-radius: 8px;
        border: 1px solid #D1D9E6; text-align: center; font-weight: 800; font-size: 16px;
    }
    
    /* 대관 카드 디자인 */
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 12px; border-radius: 8px; margin-bottom: 10px !important; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .status-badge { float: right; padding: 2px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .time-text { font-size: 15px; font-weight: bold; color: #1E3A5F; }
    .time-highlight { color: #FF4B4B; }
    .event-name { font-size: 14px; margin-top: 5px; color: #333; font-weight: 600; }
    .info-row { font-size: 12px; color: #666; margin-top: 5px; display: flex; align-items: center; gap: 5px; }
</style>
""", unsafe_allow_html=True)

# 2. 상단 필터
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
# 날짜 입력 위젯 (세션과 연동)
new_date = st.date_input("date_in", value=st.session_state.target_date, label_visibility="collapsed", key="main_date")
if new_date != st.session_state.target_date:
    st.session_state.target_date = new_date

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BU = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
cols = st.columns(2)
for i, b in enumerate(ALL_BU):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"bu_{i}"):
            selected_bu.append(b)

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 패치 함수 (SyntaxError 수정 완료)
@st.cache_data(ttl=300)
def fetch_data(dt):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": dt.strftime('%Y-%m-%d'), "end": dt.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except:
        return pd.DataFrame()

# 4. 결과 출력 섹션
if search_clicked or 'target_date' in st.session_state:
    # 전날/다음날 이동 버튼 레이아웃 (image_7fbaa4.png 스타일)
    c1, c2, c3 = st.columns([0.5, 3, 0.5])
    
    with c1:
        if st.button("◀", key="prev_day"):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()
            
    with c3:
        if st.button("▶", key="next_day"):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    with c2:
        curr = st.session_state.target_date
        w_idx = curr.weekday()
        # 요일 색상 설정
        t_color = "#1E3A5F" # 평일
        if w_idx == 5: t_color = "#0000FF" # 토요일
        elif w_idx == 6: t_color = "#FF0000" # 일요일
        
        shift = get_shift_group(curr)
        header_text = f"📋 현황 [ {curr.strftime('%Y.%m.%d')}({WEEKDAY_KR[w_idx]}) | {shift} ]"
        st.markdown(f'<div class="header-box" style="color:{t_color};">{header_text}</div>', unsafe_allow_html=True)

    # 데이터 로드 및 필터링
    df = fetch_data(st.session_state.target_date)
    if not df.empty:
        # 날짜 및 요일 필터링 로직
        target_weekday = str(st.session_state.target_date.weekday() + 1)
        
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)]
            st.markdown(f"#### 🏢 {bu}")
            
            if bu_df.empty:
                st.info("내역 없음")
                continue
                
            for _, row in bu_df.iterrows():
                # 기간 대관일 경우 요일 체크
                is_period = row['startDt'] != row['endDt']
                allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                
                if is_period and target_weekday not in allow_days:
                    continue # 해당 요일 수업이 아니면 패스
                
                status_txt = "예약확정" if row['status'] == 'Y' else "신청대기"
                wd_info = ""
                if is_period:
                    days_list = [WEEKDAY_MAP.get(d) for d in allow_days if d in WEEKDAY_MAP]
                    wd_info = f"({', '.join(days_list)})"

                st.markdown(f"""
                <div class="event-card">
                    <span class="status-badge status-y">{status_txt}</span>
                    <div class="time-text">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                    <div class="event-name">📄 {row['eventNm']}</div>
                    <div class="info-row">
                        <span>🗓️ {row['startDt']} ~ {row['endDt']} <b>{wd_info}</b></span>
                        <span style="margin-left:5px; border-left:1px solid #ddd; padding-left:5px;">👥 {row['mgDeptNm']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<center><a href='#'>▲ 맨 위로 이동</a></center>", unsafe_allow_html=True)
