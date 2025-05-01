import os
import base64
import streamlit as st
from groq import Groq
import dotenv
from io import BytesIO

# Configure the page
st.set_page_config(page_title="Text-to-Speech App", page_icon="🗣️", layout="centered")

# Load environment variables
dotenv.load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)

# Title and description
st.title("🗣️ Text-to-Speech")
st.markdown("Convert text to natural-sounding speech using Groq's TTS capabilities.")


# Create audio player function
def create_audio_player(audio_bytes):
    """Create an HTML audio player for the speech audio."""
    b64_audio = base64.b64encode(audio_bytes).decode()
    audio_player = f"""
        <audio controls autoplay>
            <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
        """
    return audio_player


# Voice selection
st.subheader("Voice Selection")
voice_options = ["Fritz-PlayAI", "Skyler-PlayAI", "Nova-PlayAI", "Cory-PlayAI"]
selected_voice = st.selectbox("Choose a voice", voice_options)

# Text input
st.subheader("Text Input")
text_input = st.text_area(
    "Enter the text you want to convert to speech:",
    "I love building and shipping new features for our users!",
    height=150,
)

# Model selection
model = "playai-tts"
response_format = "wav"

# Instructions about terms acceptance
st.sidebar.markdown("### 📝 Important Note")
st.sidebar.info(
    """
To use Groq's TTS models, your organization must first accept the terms. 
If you encounter a 'model_terms_required' error, please have your organization 
admin accept the terms at [Groq Console](https://console.groq.com/playground?model=playai-tts).
"""
)

# Generate audio button
if st.button("Generate Speech"):
    if not api_key:
        st.error("Please provide a valid Groq API key.")
    elif not text_input:
        st.error("Please enter some text to convert to speech.")
    else:
        with st.spinner("Generating speech..."):
            try:
                # Create BytesIO buffer to store audio data
                audio_buffer = BytesIO()

                # Make API call
                try:
                    response = client.audio.speech.create(
                        model=model,
                        voice=selected_voice,
                        input=text_input,
                        response_format=response_format,
                    )
                except Exception as e:
                    error_msg = str(e)
                    if "model_terms_required" in error_msg:
                        st.error(
                            """
                        ERROR: Terms acceptance required for the TTS model.
                        
                        Your organization needs to accept the terms for the PlayAI TTS model.
                        Please have the organization admin accept the terms at:
                        https://console.groq.com/playground?model=playai-tts
                        """
                        )
                        st.markdown("#### Alternative Models")
                        st.info(
                            "While waiting for terms acceptance, you might want to try using OpenAI's TTS API or other available TTS services."
                        )
                        st.stop()
                    else:
                        raise e

                # Write to buffer instead of file
                response.write_to_file(str(audio_buffer))
                # print(response.write_to_file("speech.wav"))
                # print(response.write_to_file("speech.wav").with_streaming_response.get_binary_response())
                # audio_bytes = response.write_to_file("speech.wav")
                # Reset buffer position to start
                audio_buffer.seek(0)

                # # Get audio data
                audio_bytes = audio_buffer.read()

                # Display audio player
                st.success("Speech generated successfully!")
                st.markdown(create_audio_player(audio_bytes), unsafe_allow_html=True)

                # Provide download button
                st.download_button(
                    label="Download Audio",
                    data=audio_bytes,
                    file_name="speech.wav",
                    mime="audio/wav",
                )
            except Exception as e:
                st.error(f"Error generating speech: {str(e)}")

# Advanced settings (collapsible)
with st.expander("Advanced Settings"):
    st.markdown(
        "**Note:** Additional TTS settings like speed, pitch, and other voice parameters will be added in future updates."
    )

# Information about usage
st.subheader("How to Use")
st.markdown(
    """
1. Select a voice from the dropdown menu
2. Enter or paste your text in the input box
3. Click "Generate Speech" to convert text to audio
4. Listen to the generated speech and download if needed
"""
)

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
