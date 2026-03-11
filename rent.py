import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 1. 한국 시간
KST = ZoneInfo("Asia/Seoul")
def today_kst():
    return datetime.now(KST).date()

# 2. 페이지 설정
st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

if "target_date" not in st.session_state:
    st.session_state.target_date = today_kst()

# 3. CSS
st.markdown("""
<style>

.block-container {
    padding: 1rem 0.5rem !important;
    max-width: 500px !important;
}

header {visibility:hidden;}

.title-box{
background:#F0F4FA;
border:1px solid #D1D9E6;
border-radius:12px 12px 0 0;
padding:10px;
text-align:center;
font-weight:800;
color:#1E3A5F;
margin-top:10px;
}

.date-display-box{
background:#FFFFFF;
border:1px solid #D1D9E6;
border-top:none;
border-radius:0 0 12px 12px;
padding:10px;
text-align:center;
font-size:18px;
font-weight:700;
margin-bottom:10px;
}

/* 화살표 버튼 가로 정렬 */
.nav-row{
display:flex;
justify-content:center;
gap:6px;
margin:10px 0;
}

.nav-row button{
height:38px;
font-weight:700;
}

.event-card{
border:1px solid #E0E0E0;
border-left:8px solid #2E5077;
padding:10px;
border-radius:10px;
margin-bottom:10px;
background:white;
position:relative;
}

.status-badge{
position:absolute;
top:10px;
right:10px;
background:#FFF3E0;
color:#E65100;
font-size:10px;
font-weight:bold;
padding:2px 8px;
border-radius:10px;
}

.event-footer{
border-top:1px solid #F0F0F0;
padding-top:6px;
display:flex;
justify-content:space-between;
font-size:11px;
color:#666;
}

</style>
""", unsafe_allow_html=True)

# 상단
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">🏫 성의교정 시설 대관 현황</h3>', unsafe_allow_html=True)

# 날짜 입력
st.session_state.target_date = st.date_input(
    "날짜",
    value=st.session_state.target_date,
    label_visibility="collapsed"
)

# 건물 선택
st.markdown("**🏢 건물 선택**")

buildings = [
"성의회관",
"의생명산업연구원",
"옴니버스 파크",
"옴니버스 파크 의과대학",
"옴니버스 파크 간호대학",
"대학본관",
"서울성모별관"
]

selected_bu = []

for b in buildings:
    if st.checkbox(b, value=(b in ["성의회관","의생명산업연구원"])):
        selected_bu.append(b)

# 검색 버튼
if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True

# 데이터 가져오기
@st.cache_data(ttl=300)
def get_data(d):

    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"

    params = {
        "mode":"getReservedData",
        "start":d.strftime('%Y-%m-%d'),
        "end":d.strftime('%Y-%m-%d')
    }

    try:
        res = requests.get(url,params=params,headers={"User-Agent":"Mozilla/5.0"})
        return pd.DataFrame(res.json().get("res",[]))
    except:
        return pd.DataFrame()

# 결과
if st.session_state.get("search_performed"):

    d = st.session_state.target_date
    w = ['월','화','수','목','금','토','일'][d.weekday()]

    st.markdown('<div class="title-box">성의교정 대관 현황</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="date-display-box">{d.strftime("%Y.%m.%d")} ({w})</div>',
        unsafe_allow_html=True
    )

    # 화살표 버튼
    st.markdown('<div class="nav-row">', unsafe_allow_html=True)

    col1,col2,col3 = st.columns([1,1,1])

    with col1:
        if st.button("◀",use_container_width=True):
            st.session_state.target_date -= timedelta(days=1)
            st.rerun()

    with col2:
        if st.button("오늘",use_container_width=True):
            st.session_state.target_date = today_kst()
            st.rerun()

    with col3:
        if st.button("▶",use_container_width=True):
            st.session_state.target_date += timedelta(days=1)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    df = get_data(st.session_state.target_date)

    for bu in selected_bu:

        st.markdown(
        f'<div style="font-size:16px;font-weight:bold;color:#1E3A5F;border-bottom:2px solid #1E3A5F;padding-bottom:3px;margin:15px 0 8px 0;">🏢 {bu}</div>',
        unsafe_allow_html=True)

        has_any=False

        if not df.empty:

            bu_df = df[df['buNm'].str.replace(" ","").str.contains(bu.replace(" ",""),na=False)]

            if not bu_df.empty:

                has_any=True

                for _,row in bu_df.iterrows():

                    st.markdown(f"""
                    <div class="event-card">

                        <div class="status-badge">예약</div>

                        <div style="font-size:16px;font-weight:800;color:#1E3A5F;margin-bottom:3px;">
                        📍 {row['placeNm']}
                        </div>

                        <div style="font-size:14px;font-weight:700;color:#D32F2F;margin-bottom:3px;">
                        ⏰ {row['startTime']} ~ {row['endTime']}
                        </div>

                        <div style="font-size:13px;color:#333;margin-bottom:8px;">
                        📄 {row['eventNm']}
                        </div>

                        <div class="event-footer">
                        <span>📅 {row['startDt']} ~ {row['endDt']}</span>
                        <span>👤 {row.get('mgDeptNm','')}</span>
                        </div>

                    </div>
                    """,unsafe_allow_html=True)

        if not has_any:
            st.markdown(
            '<div style="color:#999;font-size:12px;padding:15px;text-align:center;background:#FAFAFA;border:1px dashed #DDD;border-radius:10px;">내역 없음</div>',
            unsafe_allow_html=True)
