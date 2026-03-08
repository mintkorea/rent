import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS: 디자인 설정
st.markdown("""
<style>
    .main-title { font-size: 24px !important; font-weight: bold; text-align: center; color: #1E3A5F; margin-bottom: 10px; }
    .filter-container { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef; margin-bottom: 20px; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 30px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 15px; border-radius: 8px; margin-bottom: 12px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .today-card { background-color: #F8FAFF; }
    .period-card { background-color: #FFFFFF; }
    .status-badge { display: inline-block; padding: 3px 10px; font-size: 11px; border-radius: 12px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    .search-btn { margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

# 2. 검색 필터 영역
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    
    # (1) 달력 노출
    target_date = st.date_input("📅 조회 날짜 선택", value=date(2026, 3, 12))
    
    st.write("---")
    
    # (2) 건물명 체크박스 (2개 컬럼으로 나열)
    st.write("🏢 **건물 선택**")
    ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
    
    cols = st.columns(2)
    selected_buildings = []
    for i, bu in enumerate(ALL_BUILDINGS):
        if cols[i % 2].checkbox(bu, value=True, key=f"bu_{bu}"):
            selected_buildings.append(bu)
            
    st.write("---")
    
    # (3) 대관 유형 체크박스
    st.write("🗓️ **대관 유형**")
    type_cols = st.columns(2)
    show_today = type_cols[0].checkbox("📌 당일 대관", value=True)
    show_period = type_cols[1].checkbox("🗓️ 기간 대관", value=True)
    
    # (4) 검색 버튼
    search_clicked = st.button("🔍 검색하기", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 3. 데이터 로직 및 결과 출력
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

# 버튼을 눌렀을 때만 결과 노출
if search_clicked:
    df_raw = get_data(target_date)
    
    # 데이터 가공
    df = pd.DataFrame()
    if not df_raw.empty:
        temp_df = df_raw.copy()
        temp_df['startDt_dt'] = pd.to_datetime(temp_df['startDt']).dt.date
        temp_df['endDt_dt'] = pd.to_datetime(temp_df['endDt']).dt.date
        df = temp_df[(temp_df['startDt_dt'] <= target_date) & (temp_df['endDt_dt'] >= target_date)]

    st.success(f"✅ {target_date.strftime('%Y년 %m월 %d일')} 검색 결과입니다.")

    for bu in selected_buildings:
        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
        
        bu_df = pd.DataFrame()
        if not df.empty:
            bu_df = df[df['buNm'].str.contains(bu, na=False)].copy()

        if bu_df.empty:
            st.markdown('<div class="no-data" style="color:#888; font-style:italic; padding:10px;">ℹ️ 해당 날짜에 대관 내역이 없습니다.</div>', unsafe_allow_html=True)
        else:
            # 한글 우선 정렬
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
                st.markdown('<p style="font-weight:bold; margin-top:10px;">📌 당일 대관</p>', unsafe_allow_html=True)
                for _, row in today_ev.iterrows():
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    s_txt = "예약확정" if row['status'] == 'Y' else "신청대기"
                    st.markdown(f"""
                    <div class="event-card today-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div style="font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']} <span style="color:#FF4B4B; margin-left:8px;">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                        <div style="font-size:14px; margin-top:5px;">📄 {row['eventNm']}</div>
                        <div style="font-size:12px; color:#666; margin-top:5px;">👥 {row['mgDeptNm']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 기간 대관 출력
            if show_period and not period_ev.empty:
                st.markdown('<p style="font-weight:bold; margin-top:10px;">🗓️ 기간 대관</p>', unsafe_allow_html=True)
                for _, row in period_ev.iterrows():
                    s_cls = "status-y" if row['status'] == 'Y' else "status-n"
                    s_txt = "예약확정" if row['status'] == 'Y' else "신청대기"
                    st.markdown(f"""
                    <div class="event-card period-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div style="font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']} <span style="color:#FF4B4B; margin-left:8px;">⏰ {row['startTime']} ~ {row['endTime']}</span></div>
                        <div style="font-size:14px; margin-top:5px;">📄 {row['eventNm']}</div>
                        <div style="font-size:12px; color:#666; margin-top:5px;">
                            <span style="color:#d63384; font-weight:bold;">🗓️ {row['startDt']} ~ {row['endDt']}</span> | 👥 {row['mgDeptNm']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
else:
    st.info("💡 위 필터를 설정한 후 [검색하기] 버튼을 눌러주세요.")
