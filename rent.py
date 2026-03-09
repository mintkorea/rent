import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# [수정 1] CSS 스타일: 줄간격 대폭 축소 및 하단 여백 설정
st.markdown("""
<style>
    #top-anchor { position: absolute; top: 0; left: 0; }

    .block-container { 
        padding: 0.5rem 1.2rem !important; 
        max-width: 500px !important; 
    }
    header { visibility: hidden; }
    
    /* 전체적인 요소 간격 축소 */
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div[data-testid="stCheckbox"] { margin-bottom: -15px !important; } /* 체크박스 사이 간격 압축 */

    .main-title {
        font-size: 22px !important;
        font-weight: 800;
        text-align: center;
        color: #1E3A5F;
        margin: 5px 0 !important; 
    }

    /* 버튼 아래 간격 축소 */
    div.stButton {
        margin-bottom: 15px !important;
    }

    .date-display-box { 
        text-align: center; 
        background-color: #F8FAFF; 
        padding: 10px; 
        border-radius: 10px; 
        margin-bottom: 10px; 
        border: 1px solid #D1D9E6;
        line-height: 1.3;
    }
    .res-main-title { font-size: 18px; font-weight: 800; color: #1E3A5F; display: block; }
    .res-sub-title { font-size: 16px; font-weight: 700; color: #333; }
    
    .sat { color: #0000FF !important; }
    .sun { color: #FF0000 !important; }

    .sub-label {
        font-size: 16px !important;
        font-weight: 800;
        color: #2E5077;
        margin-top: 8px !important;
        margin-bottom: 2px !important;
        display: block;
    }

    .building-header { 
        font-size: 17px !important; font-weight: bold; color: #2E5077; 
        margin-top: 10px; border-bottom: 2px solid #2E5077; 
        padding-bottom: 3px; margin-bottom: 8px; 
    }

    .section-title { 
        font-size: 14px; font-weight: bold; color: #555; 
        margin: 6px 0 4px 0; padding-left: 5px; border-left: 4px solid #ccc; 
    }
    
    .event-card { 
        border: 1px solid #E0E0E0; border-left: 5px solid #2E5077; 
        padding: 6px 10px; border-radius: 5px; 
        margin-bottom: 6px !important; 
        background-color: #ffffff;
        line-height: 1.1 !important;
    }
    
    .place-name { font-size: 15px; font-weight: bold; color: #1E3A5F; }
    .time-row { font-size: 14px; font-weight: bold; color: #FF4B4B; margin-top: 1px; }
    .event-name { font-size: 13px; margin-top: 2px; color: #333; font-weight: 500; }
    
    .bottom-info { 
        font-size: 11px; color: #666; margin-top: 3px; 
        display: flex; justify-content: space-between; align-items: flex-end;
    }

    .status-badge { display: inline-block; padding: 0px 6px; font-size: 10px; border-radius: 10px; font-weight: bold; float: right; }
    .status-y { background-color: #FFF4E5; color: #B25E09; } 
    .status-n { background-color: #E8F0FE; color: #1967D2; }

    /* [수정 2] 하단 여백 추가를 위한 클래스 */
    .bottom-spacer { height: 50px; }

    .top-link-container {
        position: fixed;
        bottom: 20px;
        right: 15px;
        z-index: 999;
    }
    .top-link {
        display: block;
        background-color: #1E3A5F;
        color: white !important;
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        border-radius: 50%;
        font-size: 11px;
        font-weight: bold;
        text-decoration: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# 2. 메인 UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

st.markdown('<span class="sub-label">📅 날짜 선택</span>', unsafe_allow_html=True)
# [수정 3] 디폴트 데이를 오늘(date.today())로 설정
target_date = st.date_input("날짜", value=date.today(), label_visibility="collapsed")

st.markdown('<span class="sub-label">🏢 건물 선택</span>', unsafe_allow_html=True)
ALL_BUILDINGS = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스 파크 의과대학", "옴니버스 파크 간호대학", "대학본관", "서울성모별관"]
selected_bu = []
for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관", "의생명산업연구원"]), key=f"v48_{b}"):
        selected_bu.append(b)

st.markdown('<span class="sub-label">🗓️ 대관 유형 선택</span>', unsafe_allow_html=True)
show_today = st.checkbox("당일 대관", value=True, key="chk_today_48")
show_period = st.checkbox("기간 대관", value=True, key="chk_period_48")

st.write(" ")
st.markdown('<div id="btn-anchor"></div>', unsafe_allow_html=True)
search_clicked = st.button("🔍 검색하기", use_container_width=True, type="primary")

# 3. 데이터 로직 (생략 없음)
@st.cache_data(ttl=300)
def get_data(selected_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": selected_date.strftime('%Y-%m-%d'), "end": selected_date.strftime('%Y-%m-%d')}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        return pd.DataFrame(res.json().get('res', []))
    except: return pd.DataFrame()

def get_weekday_names(allow_day_str):
    days = {"1":"월", "2":"화", "3":"수", "4":"목", "5":"금", "6":"토", "7":"일"}
    if not allow_day_str: return ""
    day_list = [days.get(d.strip()) for d in str(allow_day_str).split(",") if days.get(d.strip())]
    return f"({','.join(day_list)})"

# 4. 결과 출력
if search_clicked:
    df_raw = get_data(target_date)
    weekday_dict = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금', 5: '토', 6: '일'}
    w_idx = target_date.weekday()
    w_str = weekday_dict[w_idx]
    w_class = "sat" if w_idx == 5 else ("sun" if w_idx == 6 else "")
    formatted_date = target_date.strftime("%Y.%m.%d")
    
    st.markdown(f"""
    <div class="date-display-box">
        <span class="res-main-title">성의교정 대관 현황</span>
        <span class="res-sub-title">{formatted_date}.<span class="{w_class}">({w_str})</span></span>
    </div>
    """, unsafe_allow_html=True)

    components.html(
        f"""<script>var element = window.parent.document.getElementById("btn-anchor"); if (element) {{ element.scrollIntoView({{behavior: "smooth", block: "start"}}); }}</script>""",
        height=0,
    )

    if not df_raw.empty:
        target_weekday = str(target_date.weekday() + 1)
        for bu in selected_bu:
            bu_df = df_raw[df_raw['buNm'].str.replace(" ", "").str.contains(bu.replace(" ", ""), na=False)].copy()
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)
            bu_df['prio'] = bu_df['placeNm'].apply(lambda x: 0 if '가' <= str(x)[0] <= '힣' else 1)
            bu_df = bu_df.sort_values(by=['prio', 'placeNm', 'startTime'])
            
            today_ev = bu_df[bu_df['startDt'] == bu_df['endDt']]
            period_ev = bu_df[bu_df['startDt'] != bu_df['endDt']]
            
            if show_today and not today_ev.empty:
                st.markdown('<div class="section-title">📌 당일 대관</div>', unsafe_allow_html=True)
                for _, row in today_ev.iterrows():
                    s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                    st.markdown(f"""
                    <div class="event-card">
                        <span class="status-badge {s_cls}">{s_txt}</span>
                        <div class="place-name">📍 {row['placeNm']}</div>
                        <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                        <div class="event-name">📄 {row['eventNm']}</div>
                        <div class="bottom-info">
                            <span class="period-label">🗓️ {row['startDt']}</span>
                            <span class="dept-label">👥 {row['mgDeptNm']}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
            
            if show_period and not period_ev.empty:
                valid_period_ev = period_ev[period_ev['allowDay'].apply(lambda x: target_weekday in [d.strip() for d in str(x).split(",")])]
                if not valid_period_ev.empty:
                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>', unsafe_allow_html=True)
                    for _, row in valid_period_ev.iterrows():
                        s_cls, s_txt = ("status-y", "예약확정") if row['status'] == 'Y' else ("status-n", "신청대기")
                        day_info = get_weekday_names(row['allowDay'])
                        st.markdown(f"""
                        <div class="event-card">
                            <span class="status-badge {s_cls}">{s_txt}</span>
                            <div class="place-name">📍 {row['placeNm']}</div>
                            <div class="time-row">⏰ {row['startTime']} ~ {row['endTime']}</div>
                            <div class="event-name">📄 {row['eventNm']}</div>
                            <div class="bottom-info">
                                <span class="period-label">🗓️ {row['startDt']} ~ {row['endDt']} {day_info}</span>
                                <span class="dept-label">👥 {row['mgDeptNm']}</span>
                            </div>
                        </div>""", unsafe_allow_html=True)
        
        # [수정 2] 최하단 여백 추가
        st.markdown('<div class="bottom-spacer"></div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="top-link-container">
                <a href="#top-anchor" class="top-link">TOP</a>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("해당 날짜에 조회된 대관 내역이 없습니다.")
        st.markdown('<div class="bottom-spacer"></div>', unsafe_allow_html=True)
