import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 배경 박스(필터 및 결과 타이틀) 및 레이아웃 최적화
st.markdown("""
<style>
    /* 전체 여백 및 폭 최적화 */
    .block-container { 
        padding: 0.5rem 0.8rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }

    /* 전체 폰트 크기 */
    html, body, [class*="st-"] { font-size: 15.5px !important; }

    /* 타이틀 공통 스타일 */
    .main-title { 
        font-size: 22px !important; 
        font-weight: 800; 
        text-align: center; 
        color: #1E3A5F; 
        margin-bottom: 0px !important; 
        padding: 5px 0;
    }
    
    /* 배경 박스 (상단 필터 및 결과 타이틀용) */
    .filter-container {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
    }

    /* 부제목 */
    .sub-header {
        font-size: 17px !important;
        font-weight: 800 !important;
        color: #2E5077;
        margin-top: 5px !important;
        margin-bottom: -10px !important;
        display: block;
    }

    /* 건물명 체크박스 */
    .stCheckbox { 
        margin-top: -6px !important; 
        margin-bottom: -6px !important; 
    }
    .stCheckbox label p { 
        font-size: 16px !important; 
        font-weight: 500;
        line-height: 1.3 !important;
    }

    /* 대관 유형 가로 강제 배치 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        width: auto !important;
        min-width: auto !important;
    }

    /* 결과 카드 디자인 */
    .building-header { 
        font-size: 19px !important; 
        font-weight: bold; 
        color: #2E5077; 
        margin-top: 15px; 
        border-bottom: 2px solid #2E5077; 
        padding-bottom: 2px; 
    }
    .event-card { 
        border: 1px solid #E0E0E0; 
        border-left: 5px solid #2E5077; 
        padding: 8px; 
        border-radius: 6px; 
        margin-bottom: 6px; 
        background-color: #ffffff; 
    }
</style>
""", unsafe_allow_html=True)

# 상단 메인 타이틀
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 2. 검색 필터 영역
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    
    # (1) 날짜 선택
    st.markdown('<span class="sub-header">📅 날짜 선택</span>', unsafe_allow_html=True)
    target_date = st.date_input("날짜 선택", value=date(2026, 3, 12), label_visibility="collapsed")

    # (2) 건물 선택
    st.markdown('<span class="sub-header">🏢 건물 선택</span>', unsafe_allow_html=True)
    ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    DEFAULT_BUILDINGS = ["성의회관", "의생명산업연구원"]

    selected_buildings = []
    for bu in ALL_BUILDINGS:
        is_default = bu in DEFAULT_BUILDINGS
        if st.checkbox(bu, value=is_default, key=f"bu_{bu}"):
            selected_buildings.append(bu)
            
    # (3) 대관 유형
    st.markdown('<span class="sub-header">🗓️ 대관 유형</span>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        show_today = st.checkbox("당일 대관", value=True)
    with c2:
        show_period = st.checkbox("기간 대관", value=False)

    # (4) 검색 버튼
    st.write("") 
    search_clicked = st.button("🔍 검색하기", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 3. 데이터 수집 함수
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, params=params, headers=headers)
        return pd.DataFrame(res.json().get('res', []))
    except:
        return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]
    else:
        df = pd.DataFrame()

    # 결과 타이틀 위 빈 라인
    st.write("") 
    
    # 결과 타이틀 영역 (박스 적용)
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    formatted_date = target_date.strftime('%m/%d')
    st.markdown(f'<div class="main-title">🏢 성의교정 대관 현황({formatted_date})</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
                if (is_period and not show_period) or (not is_period and not show_today):
                    continue
                
                s_txt = "확정" if row['status'] == 'Y' else "대기"
                period_info = f"<br><span style='font-size:12px; color:#d63384;'>🗓️ {row['startDt']}~{row['endDt']}</span>" if is_period else ""
                
                st.markdown(f"""
                <div class="event-card">
                    <b>📍 {row['placeNm']}</b> ({s_txt})<br>
                    <span style="color:#FF4B4B;">⏰ {row['startTime']}~{row['endTime']}</span>
                    {period_info}<br>
                    <span style="font-size:14px;">📄 {row['eventNm']}</span>
                </div>
                """, unsafe_allow_html=True)
