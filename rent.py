import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 박스 디자인 및 모바일 대응 가로 배치 최적화
st.markdown("""
<style>
    .block-container { padding: 0.5rem 0.8rem !important; max-width: 500px !important; }
    #MainMenu, header { visibility: hidden; }
    
    /* 회색 배경 박스 */
    .filter-container {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
    }

    /* [해결] 박스 안으로 완벽히 가두기 위한 타이틀 스타일 */
    .box-inner-title {
        font-size: 20px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin: 0 !important;
        padding: 5px 0 10px 0 !important;
        border-bottom: 1px solid #e9ecef;
        margin-bottom: 15px !important;
    }

    /* 결과 타이틀 박스용 (슬림) */
    .result-box-title {
        font-size: 18px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        padding: 5px 0 !important;
    }

    /* 소제목 */
    .sub-header {
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #2E5077;
        margin-top: 5px !important;
        margin-bottom: -5px !important;
        display: block;
    }

    /* [해결] 모바일에서 대관 유형이 잘리지 않도록 간격 조정 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 5px !important;
    }
    div[data-testid="column"] {
        min-width: fit-content !important;
        flex: 1 !important;
    }
    .stCheckbox label p { font-size: 14.5px !important; white-space: nowrap; }

    /* 결과 카드 디자인 */
    .building-header { 
        font-size: 18px !important; 
        font-weight: bold; 
        color: #2E5077; 
        margin-top: 15px; 
        border-bottom: 2px solid #2E5077; 
    }
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 8px; border-radius: 6px; margin-bottom: 6px; background-color: #ffffff; 
    }
</style>
""", unsafe_allow_html=True)

# 2. 검색 필터 영역
# [핵심] 박스 div를 먼저 열고, 그 바로 아래에 타이틀을 배치하여 '박스 안'임을 강제함
st.markdown('<div class="filter-container">', unsafe_allow_html=True)
st.markdown('<div class="box-inner-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-header">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-header">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_buildings = []
for bu in ALL_BUILDINGS:
    if st.checkbox(bu, value=(bu in ["성의회관", "의생명산업연구원"]), key=f"bu_{bu}"):
        selected_buildings.append(bu)
        
st.markdown('<span class="sub-header">🗓️ 대관 유형</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관", value=True)
with c2: show_period = st.checkbox("기간 대관", value=False)

st.write("") 
search_clicked = st.button("🔍 검색하기", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True) # 박스 닫기

# 3. 데이터 수집 함수
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
    df = pd.DataFrame()
    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]

    st.write("") 
    formatted_date = target_date.strftime('%m/%d')
    # 결과 타이틀 박스 슬림화
    st.markdown(f"""
    <div class="filter-container" style="padding: 8px !important;">
        <div class="result-box-title">🏢 성의교정 대관 현황({formatted_date})</div>
    </div>
    """, unsafe_allow_html=True)

    for bu in selected_buildings:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df[df['buNm'].str.contains(bu, na=False)].copy() if not df.empty else pd.DataFrame()
        if bu_df.empty:
            st.markdown('<div style="color:#888; font-size:14px; padding:2px 0;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
        else:
            bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            for _, row in bu_df.iterrows():
                is_period = row['startDt'] != row['endDt']
                if (is_period and not show_period) or (not is_period and not show_today): continue
                s_txt = "확정" if row['status'] == 'Y' else "대기"
                p_info = f"<br><span style='font-size:12px; color:#d63384;'>🗓️ {row['startDt']}~{row['endDt']}</span>" if is_period else ""
                st.markdown(f'<div class="event-card"><b>📍 {row["placeNm"]}</b> ({s_txt})<br><span style="color:#FF4B4B;">⏰ {row["startTime"]}~{row["endTime"]}</span>{p_info}<br><span style="font-size:14px;">📄 {row["eventNm"]}</span></div>', unsafe_allow_html=True)
