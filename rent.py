import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 카드 디자인 복구 및 여백 설정
st.markdown("""
<style>
    /* 전체 레이아웃 설정 */
    .block-container { 
        padding: 1.5rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }
    
    /* 위젯 간 간격 */
    [data-testid="stVerticalBlock"] { gap: 0.6rem !important; }

    /* [복구] 메인 타이틀 및 하단 여백 */
    .main-title {
        font-size: 24px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin-bottom: 35px !important; /* 타이틀 아래 한 줄 이상의 여백 */
    }

    /* 소제목 스타일 */
    .sub-label {
        font-size: 18px !important;
        font-weight: 800;
        color: #2E5077;
        margin-top: 5px !important;
        display: block;
    }

    /* 체크박스 폰트 */
    .stCheckbox label p { 
        font-size: 18px !important; 
        font-weight: 500 !important;
    }
    
    /* 건물명 구분선 */
    .building-header { 
        font-size: 20px !important; 
        font-weight: bold; 
        color: #2E5077; 
        margin-top: 20px !important; 
        border-bottom: 2.5px solid #2E5077; 
        padding-bottom: 5px;
        margin-bottom: 10px !important;
    }

    /* 결과 타이틀 박스 복구 */
    .result-title-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 12px !important;
        text-align: center;
        margin: 25px 0 !important;
    }

    /* [핵심 복구] 카드 스타일: 너비 100%, 좌측 강조 바, 그림자 미세 적용 */
    .event-card { 
        width: 100%;
        border: 1px solid #E0E0E0; 
        border-left: 6px solid #2E5077; 
        padding: 12px 15px; 
        border-radius: 8px; 
        margin-bottom: 10px !important; /* 카드 간 간격 약간 확보 */
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: block;
    }
    .card-place { font-size: 18px !important; font-weight: 700; color: #1E3A5F; }
    .card-time { font-size: 17px !important; color: #FF4B4B; font-weight: 600; margin: 4px 0; display: block; }
    .card-event { font-size: 16px !important; color: #444; line-height: 1.4; }
</style>
""", unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_B = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_buildings = []
for b in ALL_B:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v42_{b}"):
        selected_buildings.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_today_42")
show_period = st.checkbox("기간 대관", value=True, key="chk_period_42")

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직 (생략 - 기존과 동일)
@st.cache_data(ttl=300)
def get_data(d):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    p = {"mode": "getReservedData", "start": d.strftime('%Y-%m-%d'), "end": d.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=p, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    df = pd.DataFrame()
    if not df_raw.empty:
        t = df_raw.copy()
        t['s_dt'] = pd.to_datetime(t['startDt']).dt.date
        t['e_dt'] = pd.to_datetime(t['endDt']).dt.date
        df = t[(t['s_dt'] <= target_date) & (t['e_dt'] >= target_date)]

    st.markdown(f"""
    <div class="result-title-box">
        <span style="font-size: 20px; font-weight: 800; color: #1E3A5F;">
            🏥 성의교정 대관 현황({target_date.strftime("%m/%d")})
        </span>
    </div>
    """, unsafe_allow_html=True)

    for bu in selected_buildings:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df[df['buNm'].str.contains(bu, na=False)].copy() if not df.empty else pd.DataFrame()
        
        if bu_df.empty:
            st.markdown('<div style="color:#888; font-size:16px; padding:10px 0;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
        else:
            bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            for _, row in bu_df.iterrows():
                is_p = row['startDt'] != row['endDt']
                if (is_p and not show_period) or (not is_p and not show_today): continue
                s_txt = "확정" if row['status'] == 'Y' else "대기"
                p_info = f"<div style='font-size:14px; color:#d63384; margin-top:2px;'>🗓️ {row['startDt']}~{row['endDt']}</div>" if is_p else ""
                
                # 카드 내부 레이아웃 정돈
                st.markdown(f"""
                <div class="event-card">
                    <div class="card-place">📍 {row["placeNm"]} <span style="font-weight:500; font-size:15px; color:#666;">({s_txt})</span></div>
                    <div class="card-time">⏰ {row["startTime"]} ~ {row["endTime"]}</div>
                    <div class="card-event">📄 {row["eventNm"]}</div>
                    {p_info}
                </div>
                """, unsafe_allow_html=True)
