# ... (이전 성공한 코드의 상단 필터 및 CSS 부분 동일)

# 데이터 표시 로직 부분만 수정
if st.session_state.triggered:
    # ... (중략: 3분할 네비게이션 바 코드)

    df = fetch_data(st.session_state.search_date)
    if not df.empty:
        target_wd = str(st.session_state.search_date.weekday() + 1)
        for bu in selected_bu:
            bu_df = df[df['buNm'].str.contains(bu, na=False)]
            if bu_df.empty: continue
            
            st.markdown(f'<div class="building-title">🏢 {bu}</div>', unsafe_allow_html=True)
            for _, row in bu_df.iterrows():
                is_today = (row['startDt'] == row['endDt'])
                allow_days = [d.strip() for d in str(row.get('allowDay', '')).split(",")]
                
                # [이 부분만 추가] 예약 상태 정보 가져오기
                status = row.get('statusNm', '') 
                
                if (is_today and show_today) or (not is_today and show_period and target_wd in allow_days):
                    p_info = f"<br><small style='color:#d63384;'>🗓️ 기간대관: {row['startDt']}~{row['endDt']}</small>" if not is_today else ""
                    
                    # 카드 내부 구성에 'status'만 추가하고 디자인은 유지
                    st.markdown(f"""
                        <div class="card">
                            <div style="float:right; font-size:12px; color:#666; font-weight:bold;">[{status}]</div>
                            📍 {row['placeNm']} <span class="time-txt">⏰ {row['startTime']} ~ {row['endTime']}</span><br>
                            📄 {row['eventNm']} {p_info}
                        </div>
                    """, unsafe_allow_html=True)
# ... (이후 동일)
