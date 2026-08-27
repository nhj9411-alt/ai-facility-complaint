import streamlit as st
import time
from google import genai
from google.genai import types


# ==================================================
# 페이지 설정
# ==================================================
st.set_page_config(
    page_title="서울문화재단 AI 시설민원 지원",
    page_icon="🏢",
    layout="centered"
)


# ==================================================
# 스타일
# ==================================================
st.markdown("""
<style>

.block-container {
    max-width: 900px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}

h1 {
    margin-bottom: 0.2rem;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    height: 50px;
    font-size: 16px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# Gemini API 설정
# ==================================================
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)

except Exception:
    st.error("⚠️ Gemini API Key가 설정되지 않았습니다.")
    st.info("Streamlit → Manage app → Settings → Secrets에서 GEMINI_API_KEY를 등록해주세요.")
    st.stop()


# ==================================================
# 공간 목록
# ==================================================
spaces = [
    "본관",
    "대학로센터",
    "서울연극센터",
    "서울장애예술창작센터",
    "청년예술청",
    "연희문학창작촌",
    "서울무용센터",
    "서울연극창작센터",
    "리스테이지 서울",
    "예술교육센터 강북",
    "문래예술공장",
    "금천예술공장",
    "예술교육센터 용산",
    "노들섬",
    "서울거리예술창작센터",
    "예술교육센터 양천",
    "예술교육센터 은평",
    "신당창작아케이드",
    "예술교육센터 서초"
]


# ==================================================
# Gemini 분석 함수
# ==================================================
def analyze_with_gemini(prompt, uploaded_file=None):

    # 503 오류 발생 시 최대 3번 재시도
    max_retries = 1

    for attempt in range(max_retries):

        try:

            contents = [prompt]

            # 사진이 있는 경우 함께 전달
            if uploaded_file is not None:

                image_data = uploaded_file.getvalue()

                image_part = types.Part.from_bytes(
                    data=image_data,
                    mime_type=uploaded_file.type
                )

                contents.append(image_part)

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config={
                    "max_output_tokens": 4000,
                    "temperature": 0.3
                }
            )

            if response.text:
                return {
                    "success": True,
                    "result": response.text
                }

            return {
                "success": False,
                "message": "AI가 분석 결과를 생성하지 못했습니다. 민원 내용을 조금 더 구체적으로 입력한 후 다시 시도해주세요."
            }


        except Exception as e:

            error_message = str(e)
            
            # ==========================================
            # 429 / API 사용량 한도 초과
            # ==========================================
            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:

                return {
                    "success": False,
                    "message": """
현재 AI 분석 서비스의 일일 사용 가능 횟수를 모두 사용했습니다.

잠시 후 다시 이용하거나, 관리자에게 API 사용량 한도 확인을 요청해주세요.
"""
    }
         
            # ==========================================
            # 503 / 서버 과부하
            # ==========================================
            if "503" in error_message or "UNAVAILABLE" in error_message:

                # 아직 재시도 가능하면 대기 후 재시도
                if attempt < max_retries - 1:

                    time.sleep(3)

                    continue

                # 최종 실패 시 사용자용 안내
                return {
                    "success": False,
                    "message": """
현재 AI 분석 서비스 이용자가 많아 일시적으로 응답이 지연되고 있습니다.

잠시 후 다시 **AI 초기 대응 분석하기** 버튼을 눌러주세요.

※ 입력하신 시설 민원 내용에 문제가 있는 것이 아니며, AI 서버의 일시적인 요청 증가로 발생할 수 있습니다.
"""
                }


            # ==========================================
            # API 키 오류
            # ==========================================
            if "API_KEY" in error_message or "401" in error_message:

                return {
                    "success": False,
                    "message": """
Gemini API 연결에 문제가 발생했습니다.

관리자에게 API Key 설정 상태를 확인해달라고 요청해주세요.
"""
                }


            # ==========================================
            # 기타 오류
            # ==========================================
            return {
    "success": False,
    "message": f"""
AI 분석 중 오류가 발생했습니다.

오류 내용:
{error_message}
"""
}


    return {
        "success": False,
        "message": "AI 분석을 완료하지 못했습니다. 잠시 후 다시 시도해주세요."
    }


# ==================================================
# 화면 제목
# ==================================================
st.title("🏢 서울문화재단 AI 시설민원 지원")

st.caption(
    "시설 이상 발생 시 초기 대응을 안내하고 시설관리 담당자의 후속 조치를 지원합니다."
)

st.divider()


# ==================================================
# 시설 이상 접수
# ==================================================
st.subheader("📝 시설 이상 접수")


selected_space = st.selectbox(
    "발생공간",
    spaces
)


location = st.text_input(
    "발생 위치",
    placeholder="예: 4층 화장실 앞, 지하 1층 기계실"
)


complaint = st.text_area(
    "민원 내용",
    placeholder="예: 에어컨에서 물이 떨어져 바닥이 젖어 있습니다.",
    height=150
)


uploaded_file = st.file_uploader(
    "사진 첨부(선택)",
    type=["jpg", "jpeg", "png"]
)


# ==================================================
# AI 분석 버튼
# ==================================================
if st.button("🤖 AI 초기 대응 안내받기"):

    # 필수값 확인
    if not location.strip():

        st.warning("⚠️ 발생 위치를 입력해주세요.")

    elif not complaint.strip():

        st.warning("⚠️ 민원 내용을 입력해주세요.")

    else:

        prompt = f"""
당신은 서울문화재단 시설 이상 민원 초기 대응 지원 AI입니다.

입력된 시설 민원 내용을 분석하여 현장 담당자가 즉시 확인하고 조치할 수 있도록 안내해주세요.

[시설 민원 정보]

발생 공간: {selected_space}
발생 위치: {location}
민원 내용: {complaint}


아래 형식에 맞춰 반드시 한국어로 답변해주세요.


## 현재 상황
민원 내용을 바탕으로 현재 발생한 상황을 간단히 설명합니다.

## 공간에서 지금 할 일 ★
현장 담당자가 즉시 수행해야 할 초기 조치를 3~5개 항목으로 안내합니다.

## 확인해볼 사항
현장에서 추가로 확인해야 할 사항을 질문 형태로 안내합니다.

## 주의사항
안전사고 예방을 위해 주의해야 할 사항을 안내합니다.

## 시설 분야
- 주관 분야
- 연계 가능 분야

정확한 원인은 현장 확인이 필요하다는 점을 명확히 안내합니다.

## 시설관리 담당자 전달 내용
아래 형식으로 정리합니다.

- 발생 위치:
- 현재 증상:
- 발생 범위:
- 이용자/운영 영향:
- 현재 조치:

## 후속 조치 방향
시설관리 담당자 또는 전문 유지보수 업체가 확인해야 할 사항을 안내합니다.


중요 원칙:

1. AI가 확정적으로 고장 원인을 단정하지 않습니다.
2. 전기, 화재, 침수 등 안전 위험이 있는 경우 즉시 사용 중단 및 접근 통제를 우선 안내합니다.
3. 이용객 안전을 최우선으로 고려합니다.
4. 현장에서 직접 분해하거나 전문적인 수리를 시도하도록 안내하지 않습니다.
5. 시설관리 담당자의 현장 확인이 필요하다는 점을 명확히 합니다.
6. 답변은 실제 현장에서 바로 활용할 수 있도록 명확하고 간결하게 작성합니다.
"""

        with st.spinner("🤖 AI가 시설 민원을 분석하고 있습니다..."):

            result_data = analyze_with_gemini(
                prompt,
                uploaded_file
            )

        # ==============================================
        # 성공
        # ==============================================
        if result_data["success"]:

            st.success("AI 분석이 완료되었습니다.")

            # 사진 첨부한 경우 결과에 표시
            if uploaded_file is not None:

                st.subheader("📷 첨부 사진")

                st.image(
                    uploaded_file,
                    use_container_width=True
                )

            st.divider()

            st.subheader("🤖 AI 분석 결과")

            st.markdown(result_data["result"])

        # ==============================================
        # 실패
        # ==============================================
        else:

            st.warning("⚠️ AI 분석 서비스를 일시적으로 이용할 수 없습니다.")

            st.info(result_data["message"])

# ==================================================
# 안내 문구
# ==================================================
st.divider()

st.caption("""
※ 본 서비스는 시설관리 담당자의 판단을 지원하기 위한 초기 대응 도구이며,
정확한 원인 확인 및 전문적인 조치는 현장 확인을 통해 진행되어야 합니다.
""")
