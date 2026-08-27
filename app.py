import streamlit as st

st.set_page_config(page_title="서울문화재단 AI 시설민원 지원", page_icon="🏢", layout="centered")

st.title("🏢 서울문화재단 AI 시설민원 지원")
st.caption("시설 이상 발생 시 초기 대응을 안내하고 시설관리 담당자의 후속 조치를 지원합니다.")

spaces = [
    "본관", "대학로센터", "서울연극센터", "서울장애예술창작센터",
    "청년예술청", "연희문학창작촌", "서울무용센터", "서울연극창작센터",
    "리스테이지 서울", "예술교육센터 강북", "문래예술공장", "금천예술공장",
    "예술교육센터 용산", "노들섬", "서울거리예술창작센터",
    "예술교육센터 양천", "예술교육센터 은평", "신당창작아케이드", "예술교육센터 서초"
]

def demo_analysis(space, location, complaint):
    text = complaint.lower()
    if any(x in text for x in ["누수", "물이", "물 새", "새요", "떨어"]):
        return {
            "상황": f"{space} {location}에서 물이 발생하거나 떨어지는 것으로 보이는 시설 이상 상황입니다.",
            "할일": [
                "주변 이용자의 접근이 필요한지 확인하고 안전을 확보합니다.",
                "바닥이 젖어 있다면 미끄럼 사고가 발생하지 않도록 물기를 제거합니다.",
                "현재 상태를 사진으로 기록하고 시설관리 담당자에게 전달합니다."
            ],
            "확인": ["현재도 물이 계속 발생하고 있나요?", "주변 전기시설이나 콘센트에 물이 닿고 있나요?", "이용자 이동이나 공간 운영에 영향이 있나요?"],
            "주의": "전기시설이나 기기를 직접 분해·조작하지 마십시오.",
            "분야": "주관 분야: 기계설비 또는 건축·영선\n\n연계 가능 분야: 전기\n\n정확한 원인: 현장 확인 필요",
            "후속": "시설관리 담당자의 현장 확인 후 자체 조치 가능 여부를 판단하고, 필요 시 전문 유지보수 업체 점검을 검토합니다."
        }
    elif any(x in text for x in ["에어컨", "냉방", "냉난방"]):
        return {
            "상황": f"{space} {location}의 냉난방기 작동 이상 민원입니다.",
            "할일": ["기기의 반복적인 전원 조작은 자제합니다.", "전원 반응 및 바람 발생 여부를 확인합니다.", "현재 증상과 공간 운영 영향을 시설관리 담당자에게 전달합니다."],
            "확인": ["전원이 들어오나요?", "바람은 나오나요?", "다른 냉난방기도 같은 증상인가요?"],
            "주의": "기기를 직접 분해하거나 내부 부품을 임의로 조작하지 마십시오.",
            "분야": "주관 분야: 기계설비\n\n연계 가능 분야: 전기\n\n정확한 원인: 현장 확인 필요",
            "후속": "시설관리 담당자가 현장 확인 후 자체 조치 가능 여부를 판단하고, 필요 시 전문 유지보수 업체 점검을 검토합니다."
        }
    else:
        return {
            "상황": f"{space} {location}에서 시설 이상 민원이 접수되었습니다.",
            "할일": ["이용자 안전에 영향이 있는지 먼저 확인합니다.", "이상 상태를 사진 또는 영상으로 기록합니다.", "시설을 무리하게 조작하지 말고 시설관리 담당자에게 전달합니다."],
            "확인": ["현재 어떤 증상이 발생하나요?", "시설 사용이 가능한 상태인가요?", "이용자 또는 공간 운영에 영향이 있나요?"],
            "주의": "비전문가가 시설을 분해하거나 전문적인 수리를 시도하지 마십시오.",
            "분야": "주관 분야: 현장 확인 필요\n\n연계 가능 분야: 현장 확인 필요\n\n정확한 원인: 현장 확인 필요",
            "후속": "시설관리 담당자의 현장 확인 후 적절한 담당 분야와 조치 방법을 결정합니다."
        }

with st.form("complaint_form"):
    st.subheader("📝 시설 이상 접수")
    space = st.selectbox("발생 공간", spaces)
    location = st.text_input("발생 위치", placeholder="예: 4층 화장실 앞")
    complaint = st.text_area("민원 내용", placeholder="예: 에어컨에서 물이 떨어져요", height=130)
    photo = st.file_uploader("사진 첨부 (선택)", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("🤖 AI 초기 대응 분석하기", use_container_width=True)

if submitted:
    if not location or not complaint:
        st.error("발생 위치와 민원 내용을 입력해주세요.")
    else:
        result = demo_analysis(space, location, complaint)

        st.divider()
        st.subheader("🤖 AI 분석 결과")

        st.markdown("### 현재 상황")
        st.write(result["상황"])

        st.markdown("### 공간에서 지금 할 일 ★")
        for i, item in enumerate(result["할일"], 1):
            st.write(f"{i}. {item}")

        st.markdown("### 확인해볼 사항")
        for item in result["확인"]:
            st.write(f"• {item}")

        st.markdown("### 주의사항")
        st.warning(result["주의"])

        st.markdown("### 시설 분야")
        st.write(result["분야"])

        st.markdown("### 시설관리 담당자 전달 내용")
        st.code(
            f"""발생 위치: {space} {location}
현재 증상: {complaint}
발생 범위: 사용자 입력 내용 기준 현장 확인 필요
이용자/운영 영향: 확인 필요
실제 조치 사항: 사용자 입력 없음
미조치 또는 추가 조치 필요사항: AI 안내사항 및 현장 확인 필요"""
        )

        st.markdown("### 후속 조치 방향")
        st.write(result["후속"])

        if photo:
            st.image(photo, caption="첨부 사진")

st.divider()
st.caption("※ 본 서비스는 시설관리 담당자의 판단을 지원하기 위한 초기 대응 도구이며, 정확한 원인 및 전문적인 조치는 현장 확인을 통해 결정합니다.")
