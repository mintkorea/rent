import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 요일 계산 함수
def get_weekdays_in_period(start_str, end_str):
    try:
        start_d = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_d = datetime.strptime(end_str, '%Y-%m-%d').date()
        weekdays = ['월', '화', '수', '목', '금', '토', '일']
        found = []
        # 실제 기간 내의 요일을 정확히 추출 (수업의 경우 해당 요일 확인용)
        curr = start_d
        check_limit = 0
        while curr <= end_d and check_limit < 7:
            found.append(curr.weekday())
            curr += timedelta(days=1)
            check_limit += 1
        
        found = sorted(list(set(found)))
        return "(" + ", ".join([weekdays[d] for d in found]) + ")"
    except: return ""

# CSS: 최종 안정화된 디자인 (image_9c5306.png 스타일 기반)
st.markdown("""
<style>
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 20px !important; }
    .sub-label { font-size: 17px !important; font-weight: 800; color: #2E5077; margin-top: 10px !important; margin-bottom: 5px !important; display: block; }
    .date-display { text-align: center; font-size: 19px; font-weight: 800; background-color: #F0F2F6; padding: 12px; border-radius: 10px; margin: 20px 0; color: #1E3A5F; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 20px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .section-title { font-size: 16px; font-weight: bold; color: #444; margin: 15px 0 8px 0; padding-left: 8px; border-left: 5px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; padding: 15px; border-radius: 8px; margin-bottom: 12px !important; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .today-card { background-color: #F8FAFF; } 
    .status-badge { float: right; padding: 2px 10px; font-size: 11px; border-radius: 10px; font-weight: bold; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    .place-time { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-highlight { color: #FF4B4B; margin-left: 5px; }
    .event-name { font-size: 14px; margin-top: 6px; color: #333; font-weight: 500; }
    .info-row { font-size: 12px; color: #666; margin-top: 6px; display: flex; align-items: center; gap: 8px; }
</style>
""", unsafe_allow_html=True)

# 2. 필터 영역 (Duplicate ID 방지를 위한 고유 Key 설정)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("date_input", value=date(2026, 3, 12), label_visibility="collapsed", key="v54_date")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
cols = st.columns(2)
for i, b in enumerate(ALL_BUILDINGS):
    with cols[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v54_bu_{i}"):
            selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1: show_today = st.checkbox("당일 대관 보기", value=True, key="v54_today")
with col2: show_period = st.checkbox("기간 대관 보기", value=True, key="v54_period")

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True, key="v54_search_btn")

# 3. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    # 요청하신 타이틀 문구 형식 적용
    st.markdown(f'<div class="date-display">📋 성의교정 대관 현황({target_date.strftime("%Y.%m.%d")})</div>', unsafe_allow_html=True)

    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]

        for bu in selected_bu:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()

            if bu_df.empty:
                st.markdown('<div style="color:#888; font-style:italic; padding:10px;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
            else:
                bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
                bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
                
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
                
                if show_today and not today_ev.empty:
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in today_ev.iterrows():
                        status_cls = "status-y" if row['status'] == 'Y' else "status-n"
                        status_txt = "예약확정" if row['status'] == 'Y' else "신청대기"
                        st.markdown(f"""
                        <div class="event-card today-card">
                            <span class="status-badge {status_cls}">{status_txt}</span>
                            <div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                            <div class="info-row">👥 {row['mgDeptNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                if show_period and not period_ev.empty:
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in period_ev.iterrows():
                        status_cls = "status-y" if row['status'] == 'Y' else "status-n"
                        status_txt = "예약확정" if row['status'] == 'Y' else "신청대기"
                        weekday_info = get_weekdays_in_period(row['startDt'], row['endDt'])
                        st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge {status_cls}">{status_txt}</span>
                            <div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                            <div class="info-row">
                                <span style="color:#d63384; font-weight:bold;">🗓️ {row['startDt']} ~ {row['endDt']} {weekday_info}</span>
                                <span style="margin-left:8px; padding-left:8px; border-left:1px solid #ddd;">👥 {row['mgDeptNm']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    st.markdown("<br><center><a href='#' style='text-decoration:none; color:#1E3A5F; font-weight:bold;'>▲ 맨 위로 이동</a></center><br>", unsafe_allow_html=True)
