import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import streamlit.components.v1 as components

# 1. 페이지 설정 (원본 유지)
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS 스타일 (원본 복구 + 요일 색상 추가)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    .main-title { font-size: 24px !important; font-weight: 800; text-align: center; color: #1E3A5F; margin-bottom: 5px !important; }
    div.stButton { margin-bottom: 35px !important; }
    
    /* 타이틀 박스 */
    .date-display { text-align: center; font-size: 19px; font-weight: 800; background-color: #F0F2F6; padding: 12px; border-radius: 10px; margin-bottom: 20px; color: #1E3A5F; line-height: 1.5; }
    
    /* 요일 색상 */
    .sat-text { color: #0000FF !important; } 
    .sun-text { color: #FF0000 !important; }

    .sub-label { font-size: 18px !important; font-weight: 800; color: #2E5077; margin-top: 5px !important; display: block; }
    .building-header { font-size: 19px !important; font-weight: bold; color: #2E5077; margin-top: 15px; border-bottom: 2px solid #2E5077; padding-bottom: 5px; margin-bottom: 12px; }
    .section-title { font-size: 16px; font-weight: bold; color: #555; margin: 10px 0 6px 0; padding-left: 5px; border-left: 4px solid #ccc; }
    .event-card { border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; padding: 8px 12px; border-radius: 5px; margin-bottom: 10px !important; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; line-height: 1.2 !important; }
    .today-card { background-color: #F8FAFF; } 
    .place-name { font-size: 16px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 15px; font-weight: bold; color: #FF4B4B; margin-top: 2px; }
    .event-name { font-size: 14px; margin-top: 4px; color: #333; font-weight: 500; }
    .bottom-info { font-size: 12px; color: #666; margin-top: 5px; display: flex; justify-content: space-between; align-items: flex-end; }
    
    .status-badge { display: inline-block; padding: 1px 8px; font-size: 11px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }
    
    /* TOP 버튼 복구 */
    .top-link-container { position: fixed; bottom: 25px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 45px; height: 45px; line-height: 45px; text-align: center; border-radius: 50%; font-size: 12px; font-weight: bold; text-decoration: none !important; box-shadow: 2px 4px 8px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 메인 UI (원본 유지)
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)
st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
target_date = st.date_input("날짜", value=date(2026, 3, 12), label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"chk_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True)
show_period = st.checkbox("기간 대관", value=True)

st.write(" ")
st.markdown('<div id="btn-anchor"></div>', unsafe_allow_html=True)
search_clicked = st.button("🔍 검색하기", use_container_width=True)

# 3. 데이터 로직 (원본 유지)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    
    # 요일 처리 및 색상
    weekday_names = ["월","화","수","목","금","토","일"]
    w_idx = target_date.weekday()
    w_str = weekday_names[w_idx]
    w_class = "sat-text" if w_idx == 5 else ("sun-text" if w_idx == 6 else "")
    
    # 조 이름 추출 (가장 안전한 방식)
    group_info = "-"
    if not df_raw.empty and 'groupNm' in df_raw.columns:
        # 비어있지 않은 첫 번째 조 이름을 가져옴
        valid_groups = df_raw['groupNm'].dropna().unique()
        if len(valid_groups) > 0:
            group_info = str(valid_groups[0]).strip()

    # 타이틀 출력
    st.markdown(f"""
        <div class="date-display">
            성의교정 대관현황<br>
            {target_date.strftime("%Y.%m.%d")}<span class="{w_class}">({w_str})</span> | 근무 : {group_info}
        </div>
    """, unsafe_allow_html=True)

    # 자동 스크롤 (원본 복구)
    components.html(
        f"""
        <script>
            var element = window.parent.document.getElementById("btn-anchor");
            if (element) {{
                element.scrollIntoView({{behavior: "smooth", block: "start"}});
            }}
        </script>
        """, height=0
    )

    if not df_raw.empty:
        target_weekday = str(w_idx + 1)
        for bu in selected_bu:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            
            for _, row in bu_df.iterrows():
                is_today = (row['startDt'] == row['endDt'])
                is_period = (row['startDt'] != row['endDt'])
                
                show = False
                if is_today and show_today: show = True
                elif is_period and show_period:
                    if target_weekday in [d.strip() for d in str(row.get('allowDay','')).split(",")]:
                        show = True
                
                if show:
                    s_cls = "status-y" if row.get('status') == 'Y' else "status-n"
                    s_txt = "예약확정" if row.get('status') == 'Y' else "신청대기"
                    st.markdown(f"""
                    <div class="event-card {('today-card' if is_today else '')}">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div class="place-name">📍 {row['placeNm']}</div>
                        <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div style="font-size:14px; margin-top:4px;">📄 {row['eventNm']}</div>
                        <div class="bottom-info">
                            <span>🗓️ {row['startDt']} {('~ ' + row['endDt']) if is_period else ''}</span>
                            <span>👥 {row['mgDeptNm']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # TOP 버튼 복구
        st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
    else:
        st.info("조회된 내역이 없습니다.")
