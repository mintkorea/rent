import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 폰트 크기 확대 및 겹침 없는 밀착 레이아웃
st.markdown("""
<style>
    /* 전체 여백 및 왼쪽 마진 확보 */
    .block-container { 
        padding: 0.5rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }
    
    /* 메인 타이틀: 22px로 확대 */
    .main-title {
        font-size: 24px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin: 5px 0 15px 0 !important;
    }

    /* 소제목: 17px로 확대 및 하단 밀착 */
    .sub-label {
        font-size: 17px !important;
        font-weight: 800;
        color: #2E5077;
        margin: 8px 0 2px 0 !important;
        display: block;
    }

    /* 체크박스 텍스트: 17px로 확대 */
    .stCheckbox label p { 
        font-size: 17px !important; 
        font-weight: 500 !important;
        line-height: 1.5 !important;
    }
    
    /* 위젯 간 간격: 겹치지 않는 선에서 최소화 */
    [data-testid="stVerticalBlock"] > div { margin-bottom: 2px !important; }

    /* 결과 타이틀 박스: 폰트 확대 및 성공한 디자인 유지 */
    .result-title-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 10px !important;
        text-align: center;
        margin: 15px 0 10px 0 !important;
    }
    .result-title-text {
        font-size: 20px !important;
        font-weight: 800;
        color: #1E3A5F;
    }

    /* 건물명 헤더: 19px로 확대 및 하단 여백 제거 */
    .building-header { 
        font-size: 19px !important; 
        font-weight: bold; 
        color: #2E5077; 
        margin: 12px 0 4px 0 !important; 
        border-bottom: 2px solid #2E5077; 
        padding-bottom: 2px;
    }

    /* 결과 카드: 내부 텍스트 2pt씩 확대 */
    .event-card { 
        border: 1px solid #E0E0E0; 
        border-left: 6px solid #2E5077; 
        padding: 8px 12px; 
        border-radius: 6px; 
        margin-bottom: 5px !important; 
        background-color: #ffffff;
        line-height: 1.4 !important;
    }
    .card-place { font-size: 17px !important; font-weight: 700; }
    .card-time { font-size: 16px !important; color: #FF4B4B; font-weight: 600; }
    .card-event { font-size: 15.5px !important; color: #333; }
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
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v10_{b}"):
        selected_buildings.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관", value=True)
with c2: show_period = st.checkbox("기간 대관", value=True)

st.write(" ")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직
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

    # 성공한 타이틀 박스 (폰트 키움)
    st.markdown(f"""
    <div class="result-title-box">
        <span class="result-title-text">
            🏥 성의교정 대관 현황({target_date.strftime("%m/%d")})
        </span>
    </div>
    """, unsafe_allow_html=True)

    for bu in selected_buildings:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df[df['buNm'].str.contains(bu, na=False)].copy() if not df.empty else pd.DataFrame()
        
        if bu_df.empty:
            st.markdown('<div style="color:#888; font-size:15px; padding:2px 0;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
        else:
            bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            for _, row in bu_df.iterrows():
                is_p = row['startDt'] != row['endDt']
                if (is_p and not show_period) or (not is_p and not show_today): continue
                s_txt = "확정" if row['status'] == 'Y' else "대기"
                p_info = f"<br><span style='font-size:13px; color:#d63384;'>🗓️ {row['startDt']}~{row['endDt']}</span>" if is_p else ""
                st.markdown(f"""
                <div class="event-card">
                    <span class="card-place">📍 {row["placeNm"]}</span> ({s_txt})<br>
                    <span class="card-time">⏰ {row["startTime"]}~{row["endTime"]}</span>{p_info}<br>
                    <span class="card-event">📄 {row["eventNm"]}</span>
                </div>
                """, unsafe_allow_html=True)
