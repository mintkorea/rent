import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 배경 교정, 폰트 확대, 한 줄 정렬 및 여백 최적화
st.markdown("""
<style>
    /* 상단 및 전체 배경 여백 최적화 (틀어짐 방지) */
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 1rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }

    /* 전체 폰트 크기 확대 (기존보다 1pt 키움) */
    html, body, [class*="st-"] {
        font-size: 17px !important; 
    }

    .main-title { 
        font-size: 24px !important; 
        font-weight: bold; 
        text-align: center; 
        color: #1E3A5F; 
        margin-bottom: 10px; 
    }
    
    .filter-container { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #e9ecef; 
        margin-bottom: 15px; 
    }
    
    /* 건물명 체크박스 한 줄 정렬 및 폰트 확대 */
    .stCheckbox { 
        margin-bottom: 2px !important; 
        padding: 5px 0;
    }
    .stCheckbox label p { 
        font-size: 18px !important; 
        font-weight: 500;
    }
    
    .building-header { 
        font-size: 20px !important; 
        font-weight: bold; 
        color: #2E5077; 
        margin-top: 25px; 
        border-bottom: 2px solid #2E5077; 
        padding-bottom: 5px; 
    }

    /* 카드 디자인 최적화 */
    .event-card { 
        border: 1px solid #E0E0E0; 
        border-left: 6px solid #2E5077; 
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 12px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); 
    }
    .today-card { background-color: #F8FAFF; }
    .period-card { background-color: #FFFFFF; }
    
    .status-badge { 
        display: inline-block; 
        padding: 3px 10px; 
        font-size: 12px; 
        border-radius: 10px; 
        font-weight: bold; 
        float: right; 
    }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 2. 검색 필터 영역
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    
    # (1) 달력 상시 노출
    target_date = st.date_input("📅 날짜 선택", value=date(2026, 3, 12))
    
    st.markdown("<br>🏢 **건물 선택 (한 줄 정렬)**", unsafe_allow_html=True)
    ALL_BUILDINGS = [
        "성의회관", "의생명산업연구원", "옴니버스 파크", 
        "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", 
        "대학본관", "서울성모별관"
    ]
    # 요청하신 기본 선택 건물 (성의회관, 의생명산업연구원)
    DEFAULT_BUILDINGS = ["성의회관", "의생명산업연구원"]
    
    # (2) 건물명 체크박스 나열
    selected_buildings = []
    for bu in ALL_BUILDINGS:
        is_default = bu in DEFAULT_BUILDINGS
        if st.checkbox(bu, value=is_default, key=f"bu_{bu}"):
            selected_buildings.append(bu)
            
    st.write("---")
    
    # (3) 대관 유형 (당일대관 기본 선택)
    st.write("🗓️ **대관 유형**")
    t_col1, t_col2 = st.columns(2)
    show_today = t_col1.checkbox("📌 당일 대관", value=True)
    show_period = t_col2.checkbox("🗓️ 기간 대관", value=False)
    
    # (4) 검색 버튼
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

# 4. 결과 출력 로직
if search_clicked:
    df_raw = get_data(target_date)
    
    df = pd.DataFrame()
    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        # 선택한 날짜가 대관 기간 내에 포함되는지 확인
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]

    st.success(f"✅ {target_date.strftime('%Y년 %m월 %d일')} 검색 결과")

    for bu in selected_buildings:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = pd.DataFrame()
        if not df.empty:
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()

        if bu_df.empty:
            st.markdown('<div style="color:#888; font-size:15px; padding:10px 0;">ℹ️ 대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            # 정렬 로직: 한글 강의실 우선
            def sort_priority(x):
                if not x: return 2
                first = str(x)[0]
                return 0 if '가' <= first <= '힣' else 1
            bu_df['prio'] = bu_df['placeNm'].apply(sort_priority)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            
            today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
            period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
            
            # 당일 대관 출력
            if show_today and not today_ev.empty:
                for _, row in today_ev.iterrows():
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    s_txt = "확정" if row['status'] == 'Y' else "대기"
                    st.markdown(f"""
                    <div class="event-card today-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div style="font-weight:bold; font-size:17px; color:#1E3A5F;">📍 {row['placeNm']} <br><span style="color:#FF4B4B;">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                        <div style="font-size:15px; margin-top:8px; font-weight:500;">📄 {row['eventNm']}</div>
                        <div style="font-size:13px; color:#666; margin-top:6px;">👥 {row['mgDeptNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 기간 대관 출력
            if show_period and not period_ev.empty:
                for _, row in period_ev.iterrows():
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    s_txt = "확정" if row['status'] == 'Y' else "대기"
                    st.markdown(f"""
                    <div class="event-card period-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div style="font-weight:bold; font-size:17px; color:#1E3A5F;">📍 {row['placeNm']} <br><span style="color:#FF4B4B;">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                        <div style="font-size:15px; margin-top:8px; font-weight:500;">📄 {row['eventNm']}</div>
                        <div style="font-size:13px; color:#666; margin-top:6px;"><span style="color:#d63384; font-weight:bold;">🗓️ {row['startDt']}~{row['endDt']}</span><br>👥 {row['mgDeptNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
