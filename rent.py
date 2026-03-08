import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 성공했던 UI 복구 및 건물명 간격 최적화
st.markdown("""
<style>
    /* 전체 레이아웃: 왼쪽 마진 확보(터치 배려) 및 상단 여백 제거 */
    .block-container { 
        padding: 0.5rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }
    
    /* [원본복구] 메인 타이틀: 상자 없이 텍스트만 */
    .main-title {
        font-size: 21px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin: 5px 0 15px 0 !important;
    }

    /* 소제목: 위젯과 너무 떨어지지 않게 조정 */
    .sub-label {
        font-size: 15.5px !important;
        font-weight: 800;
        color: #2E5077;
        margin: 10px 0 2px 0 !important;
        display: block;
    }

    /* [해결] 건물명 사이 간격 초밀착: 위쪽 마진을 최소화 */
    .building-header { 
        font-size: 17px !important; 
        font-weight: bold; 
        color: #2E5077; 
        margin: 8px 0 3px 0 !important; /* 위쪽 간격을 대폭 줄였습니다 */
        border-bottom: 2px solid #2E5077; 
        padding-bottom: 2px;
    }

    /* [성공소스 유지] 결과 타이틀 박스 (image_9dce27.png 스타일) */
    .result-title-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 10px !important;
        text-align: center;
        margin: 15px 0 10px 0 !important;
    }

    /* [성공소스 유지] 대관 정보 카드 */
    .event-card { 
        border: 1px solid #E0E0E0; 
        border-left: 5px solid #2E5077; 
        padding: 6px 10px; 
        border-radius: 6px; 
        margin-bottom: 4px !important; 
        background-color: #ffffff;
    }

    /* 체크박스 터치 여백 유지 */
    .stCheckbox { margin-bottom: 3px !important; }
</style>
""", unsafe_allow_html=True)

# 2. 필터 영역 (상자 제거, 텍스트만 노출)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_B = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_buildings = []
for b in ALL_B:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v7_{b}"):
        selected_buildings.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형</span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: show_today = st.checkbox("당일 대관", value=True)
with c2: show_period = st.checkbox("기간 대관", value=True)

st.write("")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직 (생략 불가)
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

    # [수정] 성공했던 결과 타이틀 박스 원복
    f_date = target_date.strftime('%m/%d')
    st.markdown(f"""
    <div class="result-title-box">
        <span style="font-size: 18px; font-weight: 800; color: #1E3A5F;">
            🏢 성의교정 대관 현황({f_date})
        </span>
    </div>
    """, unsafe_allow_html=True)

    for bu in selected_buildings:
        # 건물명 사이의 여백을 좁게 유지
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = df[df['buNm'].str.contains(bu, na=False)].copy() if not df.empty else pd.DataFrame()
        
        if bu_df.empty:
            st.markdown('<div style="color:#888; font-size:13px; padding:2px 0;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
        else:
            bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            for _, row in bu_df.iterrows():
                is_p = row['startDt'] != row['endDt']
                if (is_p and not show_period) or (not is_p and not show_today): continue
                s_txt = "확정" if row['status'] == 'Y' else "대기"
                p_info = f"<br><span style='font-size:11px; color:#d63384;'>🗓️ {row['startDt']}~{row['endDt']}</span>" if is_p else ""
                st.markdown(f"""
                <div class="event-card">
                    <b>📍 {row["placeNm"]}</b> ({s_txt})<br>
                    <span style="color:#FF4B4B;">⏰ {row["startTime"]}~{row["endTime"]}</span>{p_info}<br>
                    <span style="font-size:13.5px;">📄 {row["eventNm"]}</span>
                </div>
                """, unsafe_allow_html=True)
