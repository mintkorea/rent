import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

st.set_page_config(page_title="성의교정 대관 조회", layout="centered")

# 세션 초기화
if 'target_date' not in st.session_state:
    st.session_state.target_date = date.today()

if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False


# NAV 처리
params = st.query_params

if "nav" in params:

    nav = params["nav"]

    if nav == "prev":
        st.session_state.target_date -= timedelta(days=1)

    if nav == "next":
        st.session_state.target_date += timedelta(days=1)

    if nav == "week_prev":
        st.session_state.target_date -= timedelta(days=7)

    if nav == "week_next":
        st.session_state.target_date += timedelta(days=7)

    if nav == "today":
        st.session_state.target_date = date.today()

    st.session_state.search_performed = True
    st.query_params.clear()
    st.rerun()


# CSS
st.markdown("""
<style>

.block-container{
    max-width:500px;
}

.main-title{
font-size:26px;
font-weight:800;
text-align:center;
color:#1E3A5F;
margin-bottom:10px;
}

.date-display-box{
text-align:center;
background:#F8FAFF;
padding:20px 10px;
border-radius:12px;
border:1px solid #D1D9E6;
margin-bottom:20px;
}

.date-row{
display:flex;
align-items:center;
justify-content:center;
gap:15px;
}

.nav-arrow{
font-size:32px;
font-weight:bold;
text-decoration:none;
color:#1E3A5F;
}

.res-sub-title{
font-size:20px;
font-weight:700;
}

.building-header{
font-size:19px;
font-weight:bold;
color:#2E5077;
margin-top:15px;
border-bottom:2px solid #2E5077;
padding-bottom:5px;
}

.section-title{
font-size:16px;
font-weight:bold;
margin:10px 0 6px 0;
}

.event-card{
border:1px solid #E0E0E0;
border-left:5px solid #2E5077;
padding:8px 12px;
border-radius:5px;
margin-bottom:10px;
background:#fff;
}

.place-name{
font-size:16px;
font-weight:bold;
}

.time-row{
font-size:15px;
font-weight:bold;
color:#FF4B4B;
}

.no-data-text{
color:#888;
font-size:14px;
padding:10px 5px;
}

</style>
""", unsafe_allow_html=True)


# 키보드 + 스와이프 이동
components.html("""
<script>

const doc = window.parent.document;

function moveDate(nav){
    const url = new URL(window.parent.location);
    url.searchParams.set("nav",nav);
    window.parent.location.href = url.toString();
}

doc.addEventListener("keydown",function(e){

    if(e.key==="ArrowLeft"){
        moveDate("prev")
    }

    if(e.key==="ArrowRight"){
        moveDate("next")
    }

    if(e.key==="ArrowUp"){
        moveDate("week_prev")
    }

    if(e.key==="ArrowDown"){
        moveDate("week_next")
    }

    if(e.key==="t" || e.key==="T"){
        moveDate("today")
    }

});

let startX=0
let endX=0

doc.addEventListener("touchstart",function(e){
startX=e.changedTouches[0].screenX
})

doc.addEventListener("touchend",function(e){

endX=e.changedTouches[0].screenX

let diff=startX-endX

if(Math.abs(diff)<50)return

if(diff>0){
moveDate("next")
}else{
moveDate("prev")
}

})

</script>
""", height=0)


# UI
st.markdown('<div class="main-title">🏫 성의교정 시설 대관 현황</div>', unsafe_allow_html=True)

target_date = st.date_input("날짜", value=st.session_state.target_date)
st.session_state.target_date = target_date


ALL_BUILDINGS = [
"성의회관",
"의생명산업연구원",
"옴니버스 파크",
"옴니버스 파크 의과대학",
"옴니버스 파크 간호대학",
"대학본관",
"서울성모별관"
]

selected_bu = []

for b in ALL_BUILDINGS:
    if st.checkbox(b, value=(b in ["성의회관","의생명산업연구원"])):
        selected_bu.append(b)


show_today = st.checkbox("당일 대관", True)
show_period = st.checkbox("기간 대관", True)


if st.button("🔍 검색하기", use_container_width=True):
    st.session_state.search_performed = True


@st.cache_data(ttl=300)
def get_data(selected_date):

    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"

    params = {
        "mode":"getReservedData",
        "start":selected_date.strftime('%Y-%m-%d'),
        "end":selected_date.strftime('%Y-%m-%d')
    }

    try:

        res=requests.get(url,params=params,headers={"User-Agent":"Mozilla/5.0"})

        return pd.DataFrame(res.json().get('res',[]))

    except:

        return pd.DataFrame()


# 결과 출력
if st.session_state.search_performed:

    df_raw = get_data(st.session_state.target_date)

    d = st.session_state.target_date

    formatted_date = d.strftime("%Y.%m.%d")


    st.markdown(f"""
    <div class="date-display-box">
        <div class="date-row">
            <a href="./?nav=prev" class="nav-arrow">←</a>
            <span class="res-sub-title">{formatted_date}</span>
            <a href="./?nav=next" class="nav-arrow">→</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


    for bu in selected_bu:

        st.markdown(f'<div class="building-header">🏢 {bu}</div>', unsafe_allow_html=True)

        has_bu_content = False

        if not df_raw.empty:

            bu_df = df_raw[df_raw['buNm'].str.replace(" ","").str.contains(bu.replace(" ",""),na=False)]

            if not bu_df.empty:

                today_ev = bu_df[bu_df['startDt']==bu_df['endDt']]
                period_ev = bu_df[bu_df['startDt']!=bu_df['endDt']]

                if show_today and not today_ev.empty:

                    has_bu_content=True

                    st.markdown('<div class="section-title">📌 당일 대관</div>',unsafe_allow_html=True)

                    for _,row in today_ev.sort_values(by='startTime').iterrows():

                        st.markdown(f"""
                        <div class="event-card">
                        <div class="place-name">📍 {row["placeNm"]}</div>
                        <div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div>
                        <div>{row["eventNm"]}</div>
                        </div>
                        """,unsafe_allow_html=True)


                if show_period and not period_ev.empty:

                    has_bu_content=True

                    st.markdown('<div class="section-title">🗓️ 기간 대관</div>',unsafe_allow_html=True)

                    for _,row in period_ev.sort_values(by='startTime').iterrows():

                        st.markdown(f"""
                        <div class="event-card">
                        <div class="place-name">📍 {row["placeNm"]}</div>
                        <div class="time-row">⏰ {row["startTime"]} ~ {row["endTime"]}</div>
                        <div>{row["eventNm"]}</div>
                        </div>
                        """,unsafe_allow_html=True)


        if not has_bu_content:

            st.markdown('<div class="no-data-text">대관 내역이 없습니다.</div>',unsafe_allow_html=True)