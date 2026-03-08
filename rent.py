import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: image_9c5306.png 수준의 디자인 복구 및 여백 미세 조정
st.markdown("""
<style>
    .block-container { 
        padding: 1rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    #MainMenu, header { visibility: hidden; }

    /* 메인 타이틀 디자인 복구 */
    .main-title {
        font-size: 24px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin-top: -10px !important;
        margin-bottom: 15px !important; 
    }

    [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }

    /* 서브 라벨 (아이콘 포함 강조) */
    .sub-label {
        font-size: 17px !important;
        font-weight: 800;
        color: #2E5077;
        margin-top: 8px !important;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    /* 결과 타이틀 (이미지 형식 반영) */
    .date-display { 
        text-align: center; font-size: 19px; font-weight: 800; 
        background-color: #F0F2F6; padding: 12px; border-radius: 10px; 
        margin: 15px 0 20px 0; color: #1E3A5F;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.05);
    }

    /* 건물 헤더 스타일 */
    .building-header { 
        font-size: 19px !important; font-weight: bold; color: #2E5077; 
        margin-top: 25px; border-bottom: 2px solid #2E5077; 
        padding-bottom: 5px; margin-bottom: 15px; 
    }

    /* 섹션 타이틀 (📌당일/🗓️기간) */
    .section-title { 
        font-size: 16px; font-weight: bold; color: #444; 
        margin: 15px 0 8px 0; padding-left: 8px; border-left: 5px solid #ccc; 
    }

    /* 카드 디자인: image_9c5306.png 스타일 복구 */
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 6px solid #2E5077; 
        padding: 15px; border-radius: 8px; 
        margin-bottom: 12px !important; 
        box-shadow: 2px 2px 8px rgba(0,0,0,0.06); 
        background-color: #ffffff;
    }
    .today-card { background-color: #F8FAFF; } 

    /* 카드 내부 텍스트 */
    .place-time { font-size: 16px; font-weight: bold; color: #1E3A5F; display: flex; align-items: center; gap: 5px; }
    .time-highlight { color: #FF4B4B; margin-left: 5px; }
    .event-name { font-size: 14px; margin-top: 6px; color: #333; font-weight: 500; }
    .info-row { font-size: 12px; color: #666; margin-top: 5px; display: flex; align-items: center; gap: 4px; }

    /* 상태 배지 */
    .status-badge { 
        float: right; padding: 3px 10px; font-size: 11px; 
        border-radius: 12px; font-weight: bold; 
    }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<div class="sub-label">📅 날짜 선택</div>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<div class="sub-label">🏢 건물 선택</div>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
# 2열로 배치하여 가독성과 공간 타협
cols_b = st.columns(2)
for i, b in enumerate(ALL_BUILDINGS):
    with cols_b[i % 2]:
        if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v52_{b}"):
            selected_bu.append(b)

st.markdown('<div class="sub-label">🗓️ 대관 유형 선택</div>', unsafe_allow_html=True)
col_t, col_p = st.columns(2)
with col_t: show_today = st.checkbox("당일 대관 보기", value=True)
with col_p: show_period = st.checkbox("기간 대관 보기", value=True)

st.write("")
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직 (생략 방지)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    p = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=p, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    formatted_date = target_date.strftime("%Y년 %m월 %d일")
    st.markdown(f'<div class="date-display">📋 {formatted_date} 대관 현황</div>', unsafe_allow_html=True)

    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]

        for bu in selected_bu:
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()

            if bu_df.empty:
                st.markdown('<div style="color:#888; font-style:italic; padding:10px;">ℹ️ 해당 건물의 대관 내역이 없습니다.</div>', unsafe_allow_html=True)
            else:
                bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
                bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
                
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
                
                # 📌 당일 대관
                if show_today and not today_ev.empty:
                    st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in today_ev.iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""
                        <div class="event-card today-card">
                            <span class="status-badge {s_cls}">{s_txt}</span>
                            <div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                            <div class="info-row">👥 {row['mgDeptNm']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 🗓️ 기간 대관
                if show_period and not period_ev.empty:
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in period_ev.iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge {s_cls}">{s_txt}</span>
                            <div class="place-time">📍 {row['placeNm']} <span class="time-highlight">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                            <div class="info-row">
                                <span style="color:#d63384; font-weight:bold;">🗓️ {row['startDt']} ~ {row['endDt']}</span>
                                <span style="margin-left:10px; padding-left:10px; border-left:1px solid #ddd;">👥 {row['mgDeptNm']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # 하단 앵커 (검색 결과로 스크롤 유도)
    st.markdown("<br><center><a href='#' style='text-decoration:none; color:#1E3A5F; font-size:14px; font-weight:bold;'>▲ 위로 이동</a></center><br>", unsafe_allow_html=True)
