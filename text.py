import streamlit as st
import time
from groq import Groq
import dotenv
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="WikiText Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS for better styling
st.markdown(
    """
<style>
    .main {
        padding: 2rem 3rem;
    }
    .stApp {
        /*background-color: #f5f7f9;*/
    }
    .stTitle {
        font-weight: 700 !important;
    }
    .chat-container {
        border-radius: 10px;
        padding: 10px;
        background-color: /*#ffffff;*/
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    .model-selector {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    div[data-testid="stVerticalBlock"] div[style*="flex-direction: column"] div[data-testid="stVerticalBlock"] {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load environment variables
dotenv.load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize Groq client
if api_key:
    client = Groq(api_key=api_key)
else:
    st.warning("No API key found. Please provide one in the sidebar.")

# Sidebar for configuration
with st.sidebar:
    st.image("https://www.faviconextractor.com/favicon/console.groq.com", width=50)
    st.title("Configuration")

    # # API Key input
    # api_key_input = st.text_input(
    #     "Groq API Key",
    #     value=api_key if api_key else "",
    #     type="password",
    #     help="Enter your Groq API key here",
    # )

    # if api_key_input != api_key and api_key_input != "":
    #     # Save API key to .env file
    #     with open(".env", "w") as f:
    #         f.write(f"API_KEY={api_key_input}")
    #     st.success("API Key saved!")
    #     api_key = api_key_input
    #     client = Groq(api_key=api_key)

    # Model selection
    selected_model = st.selectbox(
        "Select Model",
        [
            "gemma2-9b-it",
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
        ],
        index=0,
    )

    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Higher values make output more random, lower values more deterministic",
    )

    # Max tokens slider
    max_tokens = st.slider(
        "Max Tokens",
        min_value=256,
        max_value=4096,
        value=1024,
        step=128,
        help="Maximum number of tokens in the response",
    )

    # # System prompt
    # system_prompt = st.text_area(
    #     "System Prompt",
    #     value="You are a knowledgeable assistant that provides accurate, helpful information.",
    #     help="This sets the behavior of the AI assistant",
    # )

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        # st.experimental_rerun()

    # Export chat button
    if st.button("Export Chat") and st.session_state.messages:
        chat_text = "\n\n".join(
            [
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in st.session_state.messages
            ]
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="Download Chat Log",
            data=chat_text,
            file_name=f"chat_export_{timestamp}.txt",
            mime="text/plain",
        )

    st.divider()
    st.caption("© 2025 ACES Meetup Project")

# Main content area
st.markdown(
    "<h1 style='text-align: center; line-height: 1rem;'>📚 WikiText Assistant</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h4 style='text-align: center;'>Ask anything and get instant answers</h4>",
    unsafe_allow_html=True,
)


# Function to get response from Groq API
def get_response(messages, model, temp, tokens):
    try:
        # Call the Groq API to get a response
        response = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temp,
            max_completion_tokens=tokens,
            top_p=1,
            stop=None,
            stream=False,
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)


# Display chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
prompt = st.chat_input("Ask me anything...")

if prompt:
    # Add user message to history and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Prepare messages for API call
    messages = [{"role": "system", "content": prompt}]
    messages.extend(st.session_state.messages)

    # Show typing indicator
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.write("Thinking...")

        # Get response from API
        response, error = get_response(
            messages, selected_model, temperature, max_tokens
        )

        if error:
            message_placeholder.error(f"Error: {error}")
        else:
            # Simulate typing effect
            message_placeholder.empty()
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.01)  # Adjust for speed
                message_placeholder.write(full_response)

            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        """
    <div style="text-align: center;">
        <p>Powered by Groq API and Streamlit</p>
        <p style="font-size: 0.8rem;">ACES Meetup Project | Created with ❤️</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
