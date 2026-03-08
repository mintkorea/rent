import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 여백 극최소화 및 카드 디자인
st.markdown("""
<style>
    .block-container { 
        padding: 1rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }

    /* 타이틀과 상단 공백 최소화 */
    .main-title {
        font-size: 22px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin-top: -20px !important;
        margin-bottom: 5px !important; 
    }

    /* 위젯 간 간격 축소 */
    [data-testid="stVerticalBlock"] { gap: 0.2rem !important; }

    /* 라벨 폰트 크기 및 간격 조정 */
    .sub-label {
        font-size: 16px !important;
        font-weight: 800;
        color: #2E5077;
        margin-top: 5px !important;
        display: block;
    }

    /* 검색 버튼 아래 여백 */
    div.stButton { margin: 15px 0 !important; }

    /* 결과 타이틀 */
    .date-display { 
        text-align: center; font-size: 18px; font-weight: 800; 
        background-color: #F0F2F6; padding: 10px; border-radius: 10px; 
        margin: 10px 0 20px 0; color: #1E3A5F;
    }

    /* 카드 및 헤더 스타일 */
    .building-header { font-size: 18px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 3px; margin-bottom: 10px; }
    .section-title { font-size: 15px; font-weight: bold; color: #555; margin: 12px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 12px; border-radius: 5px; margin-bottom: 10px !important; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; }
    .today-card { background-color: #F8FAFF; } 
    .status-badge { display: inline-block; padding: 2px 8px; font-size: 10px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    .place-time { font-size: 15px; font-weight: bold; color: #1E3A5F; }
    .time-highlight { color: #FF4B4B; margin-left: 5px; }
</style>
""", unsafe_allow_html=True)

# 2. 메인 UI (필터 영역)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
# 촘촘한 배치를 위해 3열로 구성
cols_b = st.columns(3)
for i, b in enumerate(ALL_BUILDINGS):
    with cols_b[i % 3]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v51_{b}"):
            selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형</span>', unsafe_allow_html=True)
col_t, col_p = st.columns(2)
with col_t: show_today = st.checkbox("당일 대관", value=True)
with col_p: show_period = st.checkbox("기간 대관", value=True)

st.write("")
# 검색하기 버튼
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    p = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=p, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    # 앵커 지점 생성
    st.markdown("<div id='results'></div>", unsafe_allow_html=True)
    
    df_raw = get_data(target_date)
    formatted_date = target_date.strftime("%Y.%m.%d")
    st.markdown(f'<div class="date-display">📋 성의교정 대관 현황({formatted_date})</div>', unsafe_allow_html=True)

    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]

        for bu in selected_bu:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()

            if bu_df.empty:
                st.markdown('<div style="color:#888; font-style:italic; padding:5px 10px; font-size:14px;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
            else:
                bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
                bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
                
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
                
                if show_today and not today_ev.empty:
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in today_ev.iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""<div class="event-card today-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']}~{row['endTime']}</span></div><div style="font-size:13px; margin-top:5px; color:#333;">📄 {row['eventNm']}</div><div style="font-size:11px; color:#666; margin-top:4px;">👥 {row['mgDeptNm']}</div></div>""", unsafe_allow_html=True)
                
                if show_period and not period_ev.empty:
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in period_ev.iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""<div class="event-card"><span class="status-badge {s_cls}">{s_txt}</span><div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']}~{row['endTime']}</span></div><div style="font-size:13px; margin-top:5px; color:#333;">📄 {row['eventNm']}</div><div style="font-size:11px; color:#666; margin-top:4px;"><span style="color:#d63384; font-weight:bold;">🗓️ {row['startDt']}~{row['endDt']}</span> <span style="margin-left:8px; padding-left:8px; border-left:1px solid #ddd;">👥 {row['mgDeptNm']}</span></div></div>""", unsafe_allow_html=True)
    
    # 맨 위로 돌아가기 버튼 대신 하단에 심플한 링크 제공
    st.markdown("<br><center><a href='#' style='text-decoration:none; color:#1E3A5F; font-weight:bold;'>▲ 맨 위로 이동</a></center><br>", unsafe_allow_html=True)
