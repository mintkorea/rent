import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 각 요소별 간격 정밀 조정
st.markdown("""
<style>
    /* 상단 여백 및 전체 폭 최적화 */
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 0rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }

    /* 전체 폰트 설정 */
    html, body, [class*="st-"] { font-size: 17px !important; }

    /* 제목 설정: 아래 요소와의 간격을 달력~건물 사이 간격과 유사하게 조정 */
    .main-title { 
        font-size: 24px !important; 
        font-weight: bold; 
        text-align: center; 
        color: #1E3A5F; 
        margin-bottom: 15px !important; 
    }
    
    /* 건물 체크박스 간격 */
    .stCheckbox { 
        margin-top: -8px !important; 
        margin-bottom: -8px !important; 
    }
    .stCheckbox label p { 
        font-size: 18px !important; 
        font-weight: 500;
        line-height: 1.3 !important;
    }

    /* 구분선 및 섹션 간격 */
    hr {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    /* 검색 결과 디자인 */
    .building-header { 
        font-size: 20px !important; 
        font-weight: bold; 
        color: #2E5077; 
        margin-top: 15px; 
        border-bottom: 2px solid #2E5077; 
        padding-bottom: 3px; 
    }
    .event-card { 
        border: 1px solid #E0E0E0; 
        border-left: 6px solid #2E5077; 
        padding: 12px; 
        border-radius: 8px; 
        margin-bottom: 10px; 
        background-color: #F8FAFF;
    }
</style>
""", unsafe_allow_html=True)

# 상단 타이틀
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 2. 검색 필터 영역
with st.container():
    # (1) 날짜 선택
    target_date = st.date_input("📅 날짜 선택", value=date(2026, 3, 12))
    
    st.markdown("<div style='margin-top:10px;'><b>🏢 건물 선택</b></div>", unsafe_allow_html=True)
    ALL_BUILDINGS = [
        "성의회관", "의생명산업연구원", "옴니버스 파크", 
        "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", 
        "대학본관", "서울성모별관"
    ]
    DEFAULT_BUILDINGS = ["성의회관", "의생명산업연구원"]
    
    # (2) 건물명 체크박스
    selected_buildings = []
    for bu in ALL_BUILDINGS:
        is_default = bu in DEFAULT_BUILDINGS
        if st.checkbox(bu, value=is_default, key=f"bu_{bu}"):
            selected_buildings.append(bu)
            
    # (3) 구분선 및 대관 유형 (한 줄 배치)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<b>🗓️ 대관 유형</b>", unsafe_allow_html=True)
    
    # 컬럼을 나누어 당일/기간 대관을 한 줄에 표출
    t_col1, t_col2 = st.columns(2)
    show_today = t_col1.checkbox("📌 당일", value=True)
    show_period = t_col2.checkbox("🗓️ 기간", value=False)
    
    # (4) 검색 버튼 (간격 축소)
    st.markdown("<div style='margin-top:5px;'></div>", unsafe_allow_html=True)
    search_clicked = st.button("🔍 검색하기", use_container_width=True)

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
    
    df = pd.DataFrame()
    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]

    st.success(f"✅ {target_date.strftime('%Y년 %m월 %d일')} 검색 결과")

    for bu in selected_buildings:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = pd.DataFrame()
        if not df.empty:
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()

        if bu_df.empty:
            st.markdown('<div style="color:#888; font-size:15px; padding:5px 0;">ℹ️ 대관 내역 없음</div>', unsafe_allow_html=True)
        else:
            def sort_priority(x):
                if not x: return 2
                first = str(x)[0]
                return 0 if '가' <= first <= '힣' else 1
            bu_df['prio'] = bu_df['placeNm'].apply(sort_priority)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            
            today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
            period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
            
            if show_today and not today_ev.empty:
                for _, row in today_ev.iterrows():
                    s_txt = "확정" if row['status'] == 'Y' else "대기"
                    st.markdown(f'<div class="event-card"><b>📍 {row["placeNm"]}</b> <br><span style="color:#FF4B4B;">⏰ {row["startTime"]}~{row["endTime"]}</span> ({s_txt})<br><span style="font-size:15px;">📄 {row["eventNm"]}</span><br><span style="font-size:13px; color:#666;">👥 {row["mgDeptNm"]}</span></div>', unsafe_allow_html=True)
            
            if show_period and not period_ev.empty:
                for _, row in period_ev.iterrows():
                    s_txt = "확정" if row['status'] == 'Y' else "대기"
                    st.markdown(f'<div class="event-card"><b>📍 {row["placeNm"]}</b> <br><span style="color:#FF4B4B;">⏰ {row["startTime"]}~{row["endTime"]}</span> ({s_txt})<br><span style="font-size:15px;">📄 {row["eventNm"]}</span><br><span style="font-size:13px; color:#666;">🗓️ {row["startDt"]}~{row["endDt"]}</span></div>', unsafe_allow_html=True)
