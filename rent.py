import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# CSS 스타일 (배지 색상 대비 및 요일 색상 강제 적용)
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }
    .block-container { padding: 1rem 1.2rem !important; max-width: 500px !important; }
    header { visibility: hidden; }
    
    /* 결과 타이틀 박스 */
    .date-display-box { 
        text-align: center; background-color: #F8FAFF; 
        padding: 15px; border-radius: 12px; margin-bottom: 20px; 
        border: 1px solid #D1D9E6; line-height: 1.6;
    }
    .res-main-title { font-size: 20px; font-weight: 800; color: #1E3A5F; display: block; margin-bottom: 3px; }
    .res-sub-title { font-size: 17px; font-weight: 700; color: #333; }
    
    /* 요일 색상 정의 */
    .sat-text { color: #0000FF !important; font-weight: bold; } 
    .sun-text { color: #FF0000 !important; font-weight: bold; }

    /* 근무조 배지 스타일 */
    .g-badge {
        display: inline-block;
        padding: 2px 10px !important;
        border-radius: 6px !important;
        font-weight: 900 !important;
        margin-left: 5px;
    }
    /* 배경색과 글자색 명시적 지정 */
    .bg-A { background-color: #FFD700 !important; color: #000000 !important; } /* 황색 배경 + 검정 글씨 */
    .bg-B { background-color: #FF0000 !important; color: #FFFFFF !important; } /* 적색 배경 + 흰색 글씨 */
    .bg-C { background-color: #000080 !important; color: #FFFFFF !important; } /* 네이비 배경 + 흰색 글씨 */

    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 8px 12px; border-radius: 5px; margin-bottom: 10px !important; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); background-color: #ffffff; line-height: 1.2 !important;
    }
    .top-link-container { position: fixed; bottom: 25px; right: 20px; z-index: 999; }
    .top-link { display: block; background-color: #1E3A5F; color: white !important; width: 45px; height: 45px; line-height: 45px; text-align: center; border-radius: 50%; font-size: 12px; font-weight: bold; text-decoration: none !important; box-shadow: 2px 4px 8px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div style="text-align:center; font-size:24px; font-weight:800; color:#1E3A5F; margin-bottom:15px;">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

target_date = st.date_input("날짜 선택", value=date(2026, 3, 12), label_visibility="collapsed")

ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v48_{b}"):
        selected_bu.append(b)

show_today = st.checkbox("당일 대관", value=True, key="chk_today_48")
show_period = st.checkbox("기간 대관", value=True, key="chk_period_48")

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

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    
    # 요일 처리
    weekday_names = ['월', '화', '수', '목', '금', '토', '일']
    w_idx = target_date.weekday()
    w_str = weekday_names[w_idx]
    
    # 요일 클래스 결정
    w_span_class = ""
    if w_idx == 5: w_span_class = "sat-text"
    elif w_idx == 6: w_span_class = "sun-text"
    
    # 근무조 처리
    raw_group = df_raw.iloc[0].get('groupNm', 'C') if not df_raw.empty and 'groupNm' in df_raw.columns else "C"
    g_char = str(raw_group)[0].upper() # A, B, C 중 하나
    badge_bg_class = f"bg-{g_char}"
    group_display = f"{g_char}조"

    # 타이틀 출력
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <span class="res-sub-title">
            {target_date.strftime("%Y.%m.%d")}.<span class="{w_span_class}">({w_str})</span> | 
            근무 : <span class="g-badge {badge_bg_class}">{group_display}</span>
        </span>
    </div>
    """, unsafe_allow_html=True)

    # JavaScript 에러 방지를 위해 간단한 구조로 변경
    st.components.v1.html(
        """<script>window.parent.document.querySelector('section.main').scrollTo({top: 0, behavior: 'smooth'});</script>""",
        height=0
    )

    if not df_raw.empty:
        target_weekday_num = str(w_idx + 1)
        for bu in selected_bu:
            bu_df = df_raw[df_raw['buNm'].str.contains(bu, na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f'<div style="font-size:19px; font-weight:bold; color:#2E5077; border-bottom:2px solid #2E5077; margin-top:15px; padding-bottom:5px;">🏢 {bu}</div>', unsafe_allow_html=True)
            
            # 당일 대관
            if show_today:
                today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
                if not today_ev.empty:
                    st.markdown('<div style="font-size:16px; font-weight:bold; color:#555; margin:10px 0 6px 5px; border-left:4px solid #ccc; padding-left:5px;">📌 당일 대관</div>', unsafe_allow_html=True)
                    for _, row in today_ev.iterrows():
                        st.markdown(f"""<div class="event-card">
                            <div style="font-size:16px; font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']}</div>
                            <div style="font-size:15px; font-weight:bold; color:#FF4B4B; margin-top:2px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:14px; margin-top:4px;">📄 {row['eventNm']}</div>
                            <div class="bottom-info"><span>🗓️ {row['startDt']}</span><span>👥 {row['mgDeptNm']}</span></div>
                        </div>""", unsafe_allow_html=True)
            
            # 기간 대관
            if show_period:
                period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
                # 요일 필터링 로직
                valid_period_ev = period_ev[period_ev['allowDay'].apply(lambda x: target_weekday_num in [d.strip() for d in str(x).split(",")])]
                if not valid_period_ev.empty:
                    st.markdown('<div style="font-size:16px; font-weight:bold; color:#555; margin:10px 0 6px 5px; border-left:4px solid #ccc; padding-left:5px;">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in valid_period_ev.iterrows():
                        st.markdown(f"""<div class="event-card">
                            <div style="font-size:16px; font-weight:bold; color:#1E3A5F;">📍 {row['placeNm']}</div>
                            <div style="font-size:15px; font-weight:bold; color:#FF4B4B; margin-top:2px;">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div style="font-size:14px; margin-top:4px;">📄 {row['eventNm']}</div>
                            <div class="bottom-info"><span>🗓️ {row['startDt']} ~ {row['endDt']}</span><span>👥 {row['mgDeptNm']}</span></div>
                        </div>""", unsafe_allow_html=True)
        
        st.markdown('<div class="top-link-container"><a href="#top-anchor" class="top-link">TOP</a></div>', unsafe_allow_html=True)
    else:
        st.info("해당 날짜에 조회된 대관 내역이 없습니다.")
