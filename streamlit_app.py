import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
import re
from collections import Counter
import matplotlib.font_manager as fm
import platform

# 한글 폰트 설정
def set_korean_font():
    """시스템에 따라 한글 폰트를 설정합니다."""
    if platform.system() == 'Windows':
        font_name = 'Malgun Gothic'
    elif platform.system() == 'Darwin':  # macOS
        font_name = 'AppleGothic'
    else:  # Linux
        font_name = 'DejaVu Sans'
    
    try:
        plt.rcParams['font.family'] = font_name
    except:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    
    plt.rcParams['axes.unicode_minus'] = False

def analyze_conversation(messages):
    """대화 내용을 분석하여 많이 사용된 단어 10개를 반환합니다."""
    # 모든 메시지 내용을 합치기
    all_text = ""
    for message in messages:
        if message["role"] in ["user", "assistant"]:
            all_text += message["content"] + " "
    
    if not all_text.strip():
        return None, "분석할 대화 내용이 없습니다."
    
    # 텍스트 전처리
    # 특수문자 제거 및 소문자 변환
    text = re.sub(r'[^\w\s가-힣]', ' ', all_text)
    text = text.lower()
    
    # 단어 분리
    words = text.split()
    
    # 불용어 제거 (한국어 및 영어 기본 불용어)
    stop_words = {
        '이것', '그것', '저것', '이', '그', '저', '의', '가', '을', '를', '에', '로', '으로', 
        '과', '와', '도', '만', '에서', '부터', '까지', '한', '하는', '하고', '할', '합니다',
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall',
        'what', 'where', 'when', 'why', 'how', 'who', 'which', 'that', 'this', 'these',
        'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # 길이가 2 이상인 단어만 필터링하고 불용어 제거
    filtered_words = [word for word in words if len(word) >= 2 and word not in stop_words]
    
    if not filtered_words:
        return None, "분석할 유의미한 단어가 없습니다."
    
    # 단어 빈도 계산
    word_counts = Counter(filtered_words)
    top_10_words = word_counts.most_common(10)
    
    return top_10_words, None

def create_word_frequency_chart(word_data):
    """단어 빈도 차트를 생성합니다."""
    set_korean_font()
    
    words = [item[0] for item in word_data]
    counts = [item[1] for item in word_data]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(range(len(words)), counts, color='skyblue', edgecolor='navy', alpha=0.7)
    
    # 차트 꾸미기
    ax.set_xlabel('단어', fontsize=12, fontweight='bold')
    ax.set_ylabel('빈도', fontsize=12, fontweight='bold')
    ax.set_title('대화에서 가장 많이 사용된 단어 TOP 10', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(range(len(words)))
    ax.set_xticklabels(words, rotation=45, ha='right')
    
    # 막대 위에 빈도 수 표시
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    # 격자 추가
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    return fig

# Show title and description.
st.title("💬 MIMIC's 대화분석 챗봇 💬")
st.write(
    "이것은 OpenAI의 GPT-4o-mini 모델을 사용하여 응답을 생성하는 챗봇입니다. "
    "**'/분석'** 명령어를 입력하면 현재까지의 대화에서 가장 많이 사용된 단어 10개를 시각화해서 보여줍니다. "
    "이 앱을 사용하려면 OpenAI API 키를 제공해야 하며, 키는 [여기](https://platform.openai.com/account/api-keys)에서 얻을 수 있습니다."
)

# 사용법 안내
with st.expander("📖 사용법"):
    st.write("""
    1. OpenAI API 키를 입력하세요
    2. 평소처럼 챗봇과 대화하세요
    3. 대화 중 언제든지 **/분석** 을 입력하면 지금까지의 대화를 분석합니다
    4. 가장 많이 사용된 단어 10개가 차트로 표시됩니다
    """)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("OpenAI API 키를 입력하여 시작하세요!", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "system" and "word_analysis" in message:
                # 시각화 결과 표시
                st.pyplot(message["chart"])
                st.write(message["content"])
            else:
                st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message.
    if prompt := st.chat_input("메시지를 입력하세요... (대화 분석: /분석)"):

        # 분석 명령어 확인
        if prompt.strip() == "/분석":
            # 대화 분석 수행
            word_data, error = analyze_conversation(st.session_state.messages)
            
            if error:
                with st.chat_message("assistant"):
                    st.error(error)
                st.session_state.messages.append({"role": "assistant", "content": f"❌ {error}"})
            else:
                # 차트 생성
                fig = create_word_frequency_chart(word_data)
                
                # 분석 결과 메시지 생성
                analysis_text = "📊 **대화 분석 결과**\n\n가장 많이 사용된 단어 TOP 10:\n"
                for i, (word, count) in enumerate(word_data, 1):
                    analysis_text += f"{i}. **{word}** ({count}회)\n"
                
                with st.chat_message("assistant"):
                    st.pyplot(fig)
                    st.markdown(analysis_text)
                
                # 시각화 결과를 세션 상태에 저장 (특별한 형태로)
                st.session_state.messages.append({
                    "role": "system", 
                    "content": analysis_text,
                    "word_analysis": True,
                    "chart": fig
                })
        
        else:
            # 일반 대화 처리
            # Store and display the current prompt.
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API.
            try:
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                        if m["role"] in ["user", "assistant"]  # 시스템 메시지 제외
                    ],
                    stream=True,
                )

                # Stream the response to the chat using `st.write_stream`, then store it in 
                # session state.
                with st.chat_message("assistant"):
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"오류가 발생했습니다: {str(e)}"
                with st.chat_message("assistant"):
                    st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# 사이드바에 통계 정보 표시
with st.sidebar:
    st.header("📈 대화 통계")
    if st.session_state.get("messages"):
        user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
        assistant_messages = [m for m in st.session_state.messages if m["role"] == "assistant"]
        
        st.metric("사용자 메시지", len(user_messages))
        st.metric("AI 응답", len(assistant_messages))
        st.metric("총 대화 수", len(user_messages) + len(assistant_messages))
    else:
        st.write("아직 대화가 없습니다.")
    
    st.divider()
    
    if st.button("🗑️ 대화 기록 삭제", type="secondary"):
        st.session_state.messages = []
        st.rerun()
