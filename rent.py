import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 인위적 간격 조정 제거, 기본 개행 및 폰트 확대 유지
st.markdown("""
<style>
    /* 전체 여백 기본값 복구 (터치 마진 확보) */
    .block-container { 
        padding: 1rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }
    
    /* 메인 타이틀 */
    .main-title {
        font-size: 24px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin-bottom: 20px !important;
    }

    /* 소제목 */
    .sub-label {
        font-size: 18px !important;
        font-weight: 800;
        color: #2E5077;
        margin-top: 15px !important;
        display: block;
    }

    /* 체크박스: 기본 폰트 확대 */
    .stCheckbox label p { 
        font-size: 18px !important; 
        font-weight: 500 !important;
    }
    
    /* 건물명 헤더: 인위적 밀착 제거, 자연스러운 개행 */
    .building-header { 
        font-size: 20px !important; 
        font-weight: bold; 
        color: #2E5077; 
        margin-top: 25px !important; /* 건물 간 구분을 위해 자연스러운 간격 배치 */
        border-bottom: 2px solid #2E5077; 
        padding-bottom: 5px;
    }

    /* 결과 타이틀 박스 (성공한 디자인 유지) */
    .result-title-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 12px !important;
        text-align: center;
        margin: 20px 0 !important;
    }
    .result-title-text {
        font-size: 20px !important;
        font-weight: 800;
        color: #1E3A5F;
    }

    /* 결과 카드: 폰트 확대 및 가독성 강조 */
    .event-card { 
        border: 1px solid #E0E0E0; 
        border-left: 6px solid #2E5077; 
        padding: 10px 15px; 
        border-radius: 8px; 
        margin-top: 10px !important;
        background-color: #ffffff;
    }
    .card-place { font-size: 18px !important; font-weight: 700; }
    .card-time { font-size: 17px !important; color: #FF4B4B; font-weight: 600; }
    .card-event { font-size: 16px !important; color: #333; }
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
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v31_{b}"):
        selected_buildings.append(b)

# [수정] 대관 유형을 두 줄로 배치하여 터치 영역 확보
st.markdown('<span class="sub-label">🗓️ 대관 유형</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_today")
show_period = st.checkbox("기간 대관", value=True, key="chk_period")

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

    st.markdown(f"""
    <div class="result-title-box">
        <span class="result-title-text">
            🏥 성의교정 대관 현황({target_date.strftime("%m/%d")})
        </span>
    </div>
    """, unsafe_allow_html=True)

    for bu in selected_buildings:
        # 자연스러운 개행만 적용
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
                p_info = f"<br><span style='font-size:14px; color:#d63384;'>🗓️ {row['startDt']}~{row['endDt']}</span>" if is_p else ""
                st.markdown(f"""
                <div class="event-card">
                    <span class="card-place">📍 {row["placeNm"]}</span> ({s_txt})<br>
                    <span class="card-time">⏰ {row["startTime"]}~{row["endTime"]}</span>{p_info}<br>
                    <span class="card-event">📄 {row["eventNm"]}</span>
                </div>
                """, unsafe_allow_html=True)
