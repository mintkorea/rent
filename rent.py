import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 요청하신 고도화된 카드 스타일 및 기존 레이아웃 유지
st.markdown("""
<style>
    .block-container { 
        padding: 1rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }
    
    /* 메인 타이틀 및 요청하신 하단 여백 */
    .main-title {
        font-size: 24px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin-bottom: 35px !important; 
    }

    /* 날짜 표시 섹션 */
    .date-display { 
        text-align: center; font-size: 18px; font-weight: bold; 
        background-color: #F0F2F6; padding: 10px; border-radius: 10px; 
        margin-bottom: 20px; 
    }

    /* 소제목 스타일 */
    .sub-label {
        font-size: 18px !important;
        font-weight: 800;
        color: #2E5077;
        margin-top: 5px !important;
        display: block;
    }

    /* 건물명 헤더 */
    .building-header { 
        font-size: 19px !important; font-weight: bold; color: #2E5077; 
        margin-top: 25px; border-bottom: 2px solid #2E5077; 
        padding-bottom: 5px; margin-bottom: 15px; 
    }

    /* 섹션 타이틀 (당일/기간) */
    .section-title { 
        font-size: 16px; font-weight: bold; color: #555; 
        margin: 15px 0 10px 0; padding-left: 5px; border-left: 4px solid #ccc; 
    }
    
    /* [카드 디자인] */
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 15px; border-radius: 5px; margin-bottom: 12px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); 
    }
    .today-card { background-color: #F8FAFF; } 
    .period-card { background-color: #FFFFFF; }
    
    .no-data { color: #888; font-style: italic; padding: 10px; font-size: 14px; }
    .place-time { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-highlight { color: #FF4B4B; margin-left: 8px; }
    .event-name { font-size: 14px; margin-top: 6px; color: #333; font-weight: 500; }
    .bottom-info { font-size: 12px; color: #666; margin-top: 6px; }
    .period-label { color: #d63384; font-weight: bold; }
    .dept-label { margin-left: 10px; padding-left: 10px; border-left: 1px solid #ddd; }

    /* 상태 배지 */
    .status-badge { display: inline-block; padding: 2px 10px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v43_{b}"):
        selected_bu.append(b)

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직
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

# 4. 결과 출력 섹션 (변경 요청된 소스 반영)
if search_clicked:
    df_raw = get_data(target_date)
    st.markdown(f'<div class="date-display">📅 {target_date.strftime("%Y년 %m월 %d일")}</div>', unsafe_allow_html=True)

    df = pd.DataFrame()
    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]

    for bu in selected_bu:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        
        bu_df = pd.DataFrame()
        if not df.empty:
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()

        if bu_df.empty:
            st.markdown('<div class="no-data">ℹ️ 해당 날짜에 대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            # [정렬] 한글 우선 정렬 로직
            def sort_priority(x):
                if not x: return 2
                first = str(x)[0]
                return 0 if '가' <= first <= '힣' else 1
            
            bu_df['prio'] = bu_df['placeNm'].apply(sort_priority)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            
            today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
            period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
            
            # 1. 당일 대관
            if not today_ev.empty:
                st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                for _, row in today_ev.iterrows():
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    s_txt = "예약확정" if row['status'] == 'Y' else "신청대기"
                    st.markdown(f"""
                    <div class="event-card today-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                        <div class="event-name">📄 {row['eventNm']}</div>
                        <div class="bottom-info">👥 {row['mgDeptNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 2. 기간 대관
            if not period_ev.empty:
                st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                for _, row in period_ev.iterrows():
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    s_txt = "예약확정" if row['status'] == 'Y' else "신청대기"
                    st.markdown(f"""
                    <div class="event-card period-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                        <div class="event-name">📄 {row['eventNm']}</div>
                        <div class="bottom-info">
                            <span class="period-label">🗓️ {row['startDt']} ~ {row['endDt']}</span>
                            <span class="dept-label">👥 {row['mgDeptNm']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
