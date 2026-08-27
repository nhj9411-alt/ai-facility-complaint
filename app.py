import streamlit as st
import time
from google import genai
from google.genai import types


# ==================================================
# 기본 설정
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
    font-weight: 700;
}

div[data-testid="stAlert"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# Gemini API 설정
# ==================================================

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

except Exception:
    client = None


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
    "신당창작아케이드"
]


# ==================================================
# Gemini 분석 함수
# ==================================================

def analyze_with_gemini(prompt, uploaded_file=None):

    contents = [prompt]

    # 사진이 있는 경우 Gemini에게 전달
    if uploaded_file is not None:

        image_data = uploaded_file.getvalue()

        image_part = types.Part.from_bytes(
            data=image_data,
            mime_type=uploaded_file.type
        )

        contents.append(image_part)

    response = client.models.generate_content(

        # 속도 우선 모델
        model="gemini-2.5-flash-lite",

        contents=contents
    )

    return response.text


# ==================================================
# 화면
# ==================================================

st.title("🏢 서울문화재단 AI 시설민원 지원")

st.caption(
    "시설 이상 발생 초기 대응을 안내하고 "
    "시설관리 담당자의 조치를 지원합니다."
)


# ==================================================
# 시설 이상 접수
# ==================================================

st.subheader("📝 시설 이상 접수")


space = st.selectbox(
    "발생공간",
    spaces
)


location = st.text_input(
    "발생위치",
    placeholder="예: 1동 복도 / 화장실 / 기계실"
)


complaint = st.text_area(
    "민원 내용",
    placeholder="예: 에어컨에서 물이 떨어져요",
    height=150
)


uploaded_file = st.file_uploader(
    "사진 첨부(선택)",
    type=["jpg", "jpeg", "png"]
)


# ==================================================
# AI 분석 버튼
# ==================================================

if st.button(
    "◎ AI 초기 대응하기",
    use_container_width=True
):

    # ------------------------------
    # 입력값 확인
    # ------------------------------

    if not location.strip():

        st.warning(
            "⚠️ 발생위치를 입력해주세요."
        )


    elif not complaint.strip():

        st.warning(
            "⚠️ 민원 내용을 입력해주세요."
        )


    elif client is None:

        st.error(
            "⚠️ Gemini API Key가 설정되지 않았습니다."
        )

        st.info(
            "Streamlit Cloud → App settings → Secrets에서 "
            "GEMINI_API_KEY를 확인해주세요."
        )


    else:

        # ==================================================
        # AI 프롬프트
        # ==================================================

        prompt = f"""
당신은 서울문화재단 시설관리 초기 대응을 지원하는 AI입니다.

아래 시설 이상 민원을 분석하세요.

[발생공간]
{space}

[발생위치]
{location}

[민원 내용]
{complaint}


다음 형식으로 답변하세요.


### 1. 예상 원인

시설 이상 원인을 최대 3개까지 간결하게 작성하세요.


### 2. 즉시 확인사항

현장에서 담당자가 확인해야 할 사항을 최대 3개 작성하세요.


### 3. 초기 조치방법

시설관리 담당자가 우선적으로 할 수 있는 초기 조치를 최대 3개 작성하세요.


### 4. 담당자 전달사항

추가 확인 또는 전문업체 점검이 필요한 사항을 간결하게 작성하세요.


### 5. 안전상 주의사항

감전, 미끄럼, 낙하, 화재 등 안전 위험이 있는 경우에만 작성하세요.


중요한 조건:

- 추측을 사실처럼 단정하지 마세요.
- 전문적인 조치가 필요한 경우 반드시 현장 확인이 필요하다고 안내하세요.
- 답변은 시설관리 실무자가 바로 활용할 수 있도록 간결하게 작성하세요.
- 전체 답변은 너무 길지 않게 작성하세요.
"""


        # ==================================================
        # AI 분석
        # ==================================================

        try:

            start_time = time.time()

            with st.spinner(
                "🤖 AI가 시설 이상 내용을 분석하고 있습니다..."
            ):

                result = analyze_with_gemini(
                    prompt,
                    uploaded_file
                )

            end_time = time.time()

            analysis_time = round(
                end_time - start_time,
                1
            )


            # ==================================================
            # 결과
            # ==================================================

            st.divider()

            st.subheader("🤖 AI 분석 결과")

            st.caption(
                f"분석 완료 · {analysis_time}초"
            )

            st.success(
                "AI 분석이 완료되었습니다."
            )

            st.markdown(result)


        # ==================================================
        # 오류 처리
        # ==================================================

        except Exception as e:

            error_message = str(e)

            # 503 오류
            if "503" in error_message or "UNAVAILABLE" in error_message:

                st.warning(
                    "⚠️ AI 분석 서비스를 일시적으로 이용할 수 없습니다."
                )

                st.info("""
AI 분석 서버에 일시적인 오류가 발생했습니다.

잠시 후 다시 시도해주세요.

문제가 계속될 경우 시설관리 담당자에게 직접 문의해주세요.
""")


            # API Key 오류
            elif "API_KEY" in error_message or "401" in error_message:

                st.error(
                    "⚠️ Gemini API 인증에 실패했습니다."
                )

                st.info(
                    "Streamlit Secrets의 GEMINI_API_KEY를 확인해주세요."
                )


            # 기타 오류
            else:

                st.warning(
                    "⚠️ AI 분석 중 일시적인 오류가 발생했습니다."
                )

                st.info("""
잠시 후 다시 시도해주세요.

문제가 계속될 경우 시설관리 담당자에게 직접 문의해주세요.
""")


# ==================================================
# 안내 문구
# ==================================================

st.divider()

st.caption(
    "※ 본 서비스는 시설관리 담당자의 판단을 지원하기 위한 초기 대응 도구이며, "
    "정확한 원인 확인 및 전문적인 조치는 현장 확인을 통해 진행되어야 합니다."
)
