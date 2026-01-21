import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# 1. 환경 설정 및 데이터 파일 로드
DB_FILE = "advanced_health_data.csv"

def load_data():
    if os.path.isfile(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame()

def save_data(data_dict):
    df = load_data()
    new_df = pd.DataFrame([data_dict])
    updated_df = pd.concat([df, new_df], ignore_index=True)
    updated_df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    

# 3. 메인 UI 설정
st.set_page_config(page_title="AI Smart Health", layout="wide")

# 사이드바: 프로필 및 음악 제어
with st.sidebar:
    st.title("👤 사용자 프로필")
    gender = st.radio("성별", ["남성", "여성"])
    age = st.number_input("나이", min_value=1, max_value=120, value=30)
    activity_level = st.select_slider(
        "평소 활동량",
        options=["매우 적음", "적음", "보통", "많음", "매우 많음"],
        value="보통"
    )
    st.divider()
    st.header("📝 오늘의 기록")
    height = st.number_input("키(cm)", value=175.0)
    weight = st.number_input("현재 체중(kg)", value=70.0)
    sugar = st.number_input("공복 혈당(mg/dL)", value=95)
    bp_sys = st.number_input("최고 혈압(수축기)", value=115)
    bp_dia = st.number_input("최저 혈압(이완기)", value=75)
    steps = st.number_input("오늘 걸음 수", value=5000)
    water = st.slider("물 섭취량 (컵/200ml)", 0, 20, 5)
    
    if st.button("🚀 데이터 분석 및 저장"):
        # BMI 계산
        bmi = weight / ((height/100)**2)
        
        # BMR 계산 (Mifflin-St Jeor 공식)
        if gender == "남성":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
            
        # 건강 점수 계산 (자체 로직: BMI, 혈압, 혈당 기반)
        score = 100
        if not (18.5 <= bmi <= 23): score -= 10
        if sugar >= 100: score -= 15
        if bp_sys >= 120 or bp_dia >= 80: score -= 15
        if steps < 6000: score -= 5
        
        save_data({
            "날짜": datetime.now().strftime("%Y-%m-%d"),
            "키": height, "체중": weight, "BMI": round(bmi, 2),
            "BMR": round(bmr, 1), "혈당": sugar, "수축기": bp_sys, 
            "이완기": bp_dia, "걸음수": steps, "물섭취": water, "점수": score
        })
        st.success("오늘의 기록이 저장되었습니다!")
        st.rerun()

# 메인 화면: 대시보드
st.title("🏥 AI 개인별 맞춤 건강 대시보드")
df_history = load_data()

if not df_history.empty:
    latest = df_history.iloc[-1]
    
    # 상단 요약 지표
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("종합 건강 점수", f"{int(latest['점수'])}점", f"{int(latest['점수']-70) if latest['점수']>70 else -10}%")
    c2.metric("나의 BMI", f"{latest['BMI']}", "정상" if 18.5 <= latest['BMI'] <= 23 else "관리필요")
    c3.metric("기초대사량(BMR)", f"{latest['BMR']} kcal")
    c4.metric("오늘의 걸음", f"{int(latest['걸음수'])}보", f"{int(latest['걸음수']-10000)} (목표 1만)")

    st.divider()
    
    # 중앙 분석 섹션
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📉 체중 및 건강 점수 변화 추이")
        fig = px.line(df_history, x="날짜", y=["체중", "점수"], markers=True, 
                      title="체중(kg) 및 건강 점수 변화")
        st.plotly_chart(fig, use_container_width=True)
        
    with col_right:
        st.subheader("💡 AI 맞춤 처방")
        if latest['점수'] >= 90:
            st.success("최상의 상태입니다! 현재 습관을 유지하세요.")
        elif latest['점수'] >= 70:
            st.info("비교적 양호합니다. 걸음수와 물 섭취량을 조금 더 늘려보세요.")
        else:
            st.warning("집중 관리가 필요합니다. 특히 혈압과 식단에 유의하세요.")
            
        st.write(f"**권장 수분 섭취:** {latest['체중']*30/1000:.1f}L (약 {int(latest['체중']*30/200)}컵)")
        st.progress(min(int(latest['물섭취']) / 10, 1.0), text=f"물 섭취 달성도 ({int(latest['물섭취'])}/10)")

    # 하단 데이터 로그
    with st.expander("📋 전체 건강 기록 로그 확인"):
        st.table(df_history.sort_values("날짜", ascending=False))

else:
    st.info("왼쪽 사이드바에서 정보를 입력하고 '데이터 분석 및 저장' 버튼을 눌러주세요.")
    