import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 초정밀 여백 및 간격 조정
st.markdown("""
<style>
    /* 전체 상단 여백 최소화 */
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; }
    header { visibility: hidden; }
    
    /* 타이틀 및 달력 간격 축소 */
    .main-title { font-size: 20px !important; font-weight: bold; text-align: center; color: #1E3A5F; margin-bottom: -10px; }
    .filter-container { background-color: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #e9ecef; margin-bottom: 10px; }
    
    /* 체크박스 영역 촘촘하게 (모바일 최적화) */
    .stCheckbox { margin-bottom: -22px !important; }
    .stCheckbox label p { font-size: 14px !important; line-height: 1.2 !important; }
    
    /* 구분선 및 섹션 제목 간격 축소 */
    hr { margin: 10px 0 !important; }
    .section-label { font-size: 14px; font-weight: bold; color: #2E5077; margin-bottom: 5px; }

    /* 결과 카드 디자인 */
    .building-header { font-size: 17px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 2px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 10px; border-radius: 8px; margin-bottom: 8px; }
    .status-badge { display: inline-block; padding: 1px 6px; font-size: 10px; border-radius: 8px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 2. 검색 필터 영역
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    
    # 달력 노출 (레이블 최소화)
    target_date = st.date_input("📅 날짜 선택", value=date(2026, 3, 12), label_visibility="collapsed")
    
    st.markdown('<p class="section-label">🏢 건물 선택</p>', unsafe_allow_html=True)
    
    # 건물 리스트 및 기본값 설정
    ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    DEFAULT_BUILDINGS = ["성의회관", "의생명산업연구원"]
    
    cols = st.columns(2)
    selected_buildings = []
    for i, bu in enumerate(ALL_BUILDINGS):
        is_default = bu in DEFAULT_BUILDINGS
        if cols[i % 2].checkbox(bu, value=is_default, key=f"bu_{bu}"):
            selected_buildings.append(bu)
            
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown('<p class="section-label">🗓️ 대관 유형</p>', unsafe_allow_html=True)
    type_cols = st.columns(2)
    # 당일대관 기본 선택, 기간대관 기본 해제
    show_today = type_cols[0].checkbox("📌 당일 대관", value=True)
    show_period = type_cols[1].checkbox("🗓️ 기간 대관", value=False)
    
    # 검색 버튼
    search_clicked = st.button("🔍 검색하기", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

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

# 검색 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    
    df = pd.DataFrame()
    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]

    st.success(f"✅ {target_date.strftime('%m/%d')} 검색 결과")

    for bu in selected_buildings:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        bu_df = pd.DataFrame()
        if not df.empty:
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()

        if bu_df.empty:
            st.markdown('<div style="color:#888; font-size:12px; padding:5px 0;">ℹ️ 내역 없음</div>', unsafe_allow_html=True)
        else:
            # 정렬 로직
            def sort_priority(x):
                if not x: return 2
                first = str(x)[0]
                return 0 if '가' <= first <= '힣' else 1
            bu_df['prio'] = bu_df['placeNm'].apply(sort_priority)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            
            today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
            period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
            
            # 필터링된 결과 노출
            if show_today and not today_ev.empty:
                for _, row in today_ev.iterrows():
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    s_txt = "확정" if row['status'] == 'Y' else "대기"
                    st.markdown(f'<div class="event-card" style="background-color:#F8FAFF;"><span class="status-badge {s_cls}">{s_txt}</span><div style="font-weight:bold; font-size:14px;">📍 {row["placeNm"]} <span style="color:#FF4B4B; margin-left:5px;">{row["startTime"]}~{row["endTime"]}</span></div><div style="font-size:13px; margin-top:3px;">📄 {row["eventNm"]}</div><div style="font-size:11px; color:#666; margin-top:3px;">👥 {row["mgDeptNm"]}</div></div>', unsafe_allow_html=True)
            
            if show_period and not period_ev.empty:
                for _, row in period_ev.iterrows():
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    s_txt = "확정" if row['status'] == 'Y' else "대기"
                    st.markdown(f'<div class="event-card" style="background-color:#FFFFFF;"><span class="status-badge {s_cls}">{s_txt}</span><div style="font-weight:bold; font-size:14px;">📍 {row["placeNm"]} <span style="color:#FF4B4B; margin-left:5px;">{row["startTime"]}~{row["endTime"]}</span></div><div style="font-size:13px; margin-top:3px;">📄 {row["eventNm"]}</div><div style="font-size:11px; color:#666; margin-top:3px;"><span style="color:#d63384; font-weight:bold;">🗓️ {row["startDt"]}~{row["endDt"]}</span> | {row["mgDeptNm"]}</div></div>', unsafe_allow_html=True)
else:
    st.info("💡 필터 설정 후 [검색하기]를 눌러주세요.")
