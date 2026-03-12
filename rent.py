    # --- [수정 반영] 6. 강의실 개방 요청 일람 섹션 ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="building-header">🔓 강의실 개방 요청 일람</div>', unsafe_allow_html=True)
    
    v_wd = d.isoweekday() # 1:월 ~ 7:일
    is_weekend = v_wd in [6, 7]
    
    # 기간 조건 (4층: 3/2~4/30, 801호: 2/7~4/24)
    is_p_4th = (date(d.year, 3, 2) <= d <= date(d.year, 4, 30))
    is_p_801 = (date(d.year, 2, 7) <= d <= date(d.year, 4, 24))

    # 1. 서울성모별관 카드
    bg_rooms = ["1201, 1202, 1203, 1204, 1205, 1206호"]
    if not is_weekend:
        bg_status = "평일: 오전 개방 / 오후 폐쇄"
        bg_note = "1206호 매주 금요일 10시 교육 예정 (순찰 시 확인)" if v_wd == 5 else "특이사항 없음"
    else:
        bg_status = "주말: 대관 현황 확인 후 개방"
        bg_note = "주말(토, 일) 지침 적용"
    
    st.markdown(f"""
    <div class="open-card">
        <div class="open-bu-title">🏢 서울성모별관</div>
        <div class="open-room-item">✅ {bg_rooms[0]}</div>
        <div class="open-room-item" style="color:#1E3A5F; font-weight:bold; margin-top:3px;">⏱️ {bg_status}</div>
        <div class="open-note">💡 {bg_note}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 성의회관 카드
    sh_items = []
    
    # 주중/주말 기본 개방 규칙 (421, 422, 521, 522)
    if not is_weekend:
        sh_items.append({
            "room": "421, 422, 521, 522호",
            "time": "주중: 오전 개방 / 오후 원칙적 폐쇄",
            "note": "학생 요청 시 무리하게 퇴실시키지 말 것"
        })
    
    # 기간제 개방 (402~407)
    if is_p_4th:
        sh_items.append({
            "room": "402, 403, 404, 405, 406, 407호",
            "time": "08:00 ~ 20:00 개방",
            "note": "첫 순찰 시 개방 / 마지막 순찰 시 잠금"
        })
        
    # 기간제 개방 (801호)
    if is_p_801:
        sh_items.append({
            "room": "801호 (대강당)",
            "time": "09:00 ~ 21:00 개방",
            "note": "평일 야간 21:00 폐쇄만 수행 (직원이 개방)"
        })

    # 요일별 특수 개방
    if v_wd == 2: # 화
        sh_items.append({"room": "502-1호", "time": "19:00 ~ 22:00", "note": "대학원 박사과정 기간 개방"})
    elif v_wd == 3: # 수
        sh_items.append({"room": "506호 (솔로몬의 방)", "time": "15:00경 개방", "note": "매주 수요일 지침"})
        sh_items.append({"room": "502-1호", "time": "19:00 ~ 22:00", "note": "대학원 박사과정 기간 개방"})

    if sh_items:
        rooms_html = "".join([f"""
            <div style="margin-bottom:10px; border-bottom:1px dashed #eee; padding-bottom:5px;">
                <div style="font-weight:bold; color:#333;">• {item['room']}</div>
                <div style="font-size:12px; color:#FF4B4B;">⏱️ {item['time']}</div>
                <div style="font-size:11px; color:#666;">└ {item['note']}</div>
            </div>
        """ for item in sh_items])
        
        st.markdown(f"""
        <div class="open-card">
            <div class="open-bu-title">🏢 성의회관</div>
            <div class="open-room-item">{rooms_html}</div>
        </div>
        """, unsafe_allow_html=True)
