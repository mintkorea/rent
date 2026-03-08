import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS 및 스크롤 스크립트
st.markdown("""
<style>
    .block-container { 
        padding: 1rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }
    
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }

    .main-title {
        font-size: 24px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin-bottom: 5px !important; 
    }

    div.stButton {
        margin-bottom: 35px !important;
    }

    .date-display { 
        text-align: center; font-size: 19px; font-weight: 800; 
        background-color: #F0F2F6; padding: 12px; border-radius: 10px; 
        margin-bottom: 20px; 
        color: #1E3A5F;
    }

    .sub-label {
        font-size: 18px !important;
        font-weight: 800;
        color: #2E5077;
        margin-top: 5px !important;
        display: block;
    }

    .building-header { 
        font-size: 19px !important; font-weight: bold; color: #2E5077; 
        margin-top: 15px; border-bottom: 2px solid #2E5077; 
        padding-bottom: 5px; margin-bottom: 12px; 
    }

    .section-title { 
        font-size: 16px; font-weight: bold; color: #555; 
        margin: 15px 0 8px 0; padding-left: 5px; border-left: 4px solid #ccc; 
    }
    
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 15px; border-radius: 5px; 
        margin-bottom: 12px !important; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); 
        background-color: #ffffff;
    }
    .today-card { background-color: #F8FAFF; } 
    
    .place-time { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-highlight { color: #FF4B4B; margin-left: 8px; }
    .event-name { font-size: 14px; margin-top: 6px; color: #333; font-weight: 500; }
    .bottom-info { font-size: 12px; color: #666; margin-top: 6px; }
    .period-label { color: #d63384; font-weight: bold; }
    .dept-label { margin-left: 10px; padding-left: 10px; border-left: 1px solid #ddd; }

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
# 사용자님의 원본 배열(수직) 유지
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v48_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_today_48")
show_period = st.checkbox("기간 대관", value=True, key="chk_period_48")

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력 및 자동 스크롤
if search_clicked:
    st.markdown('<div id="result-section"></div>', unsafe_allow_html=True)
    
    df_raw = get_data(target_date)
    # 현재 선택 날짜의 요일 인덱스 (API 기준 1~7)
    target_weekday = str(target_date.weekday() + 1)
    
    formatted_date = target_date.strftime("%Y.%m.%d")
    st.markdown(f'<div class="date-display">📋 성의교정 대관 현황({formatted_date})</div>', unsafe_allow_html=True)

    components.html(
        f"""
        <script>
            var element = window.parent.document.getElementById("result-section");
            if (element) {{
                element.scrollIntoView({{behavior: "smooth", block: "start"}});
            }}
        </script>
        """,
        height=0,
    )

    if not df_raw.empty:
        for bu in selected_bu:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)].copy()

            if bu_df.empty:
                continue
            else:
                st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
                bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
                bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
                
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
                
                # 1. 당일 대관 출력
                if show_today and not today_ev.empty:
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in today_ev.iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""
                        <div class="event-card today-card">
                            <span class="status-badge {s_cls}">{s_txt}</span>
                            <div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                            <div class="bottom-info">👥 {row['mgDeptNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 2. 기간 대관 출력 (요일 필터링 로직 적용)
                if show_period and not period_ev.empty:
                    # 요일 체크: allowDay에 현재 요일 코드가 포함된 것만 추출
                    valid_period_ev = period_ev[period_ev['allowDay'].apply(lambda x: target_weekday in [d.strip() for d in str(x).split(",")])]
                    
                    if not valid_period_ev.empty:
                        st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                        for _, row in valid_period_ev.iterrows():
                            s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                            st.markdown(f"""
                            <div class="event-card">
                                <span class="status-badge {s_cls}">{s_txt}</span>
                                <div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                                <div class="event-name">📄 {row['eventNm']}</div>
                                <div class="bottom-info">
                                    <span class="period-label">🗓️ {row['startDt']} ~ {row['endDt']}</span>
                                    <span class="dept-label">👥 {row['mgDeptNm']}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
    else:
        st.info("해당 날짜에 조회된 대관 내역이 없습니다.")
