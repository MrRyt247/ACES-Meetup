import streamlit as st
import requests
from PIL import Image
import io
import base64
from groq import Groq
import dotenv
import os

# Page configuration
st.set_page_config(page_title="Vision Image Analyzer", layout="wide")

# Load environment variables
dotenv.load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)

# Title and description
st.title("🔍 Vision Image Analyzer")
st.subheader("Analyze images using Groq's vision capabilities")
st.markdown("Upload an image or provide a URL to analyze what's in the image.")


# Function to get base64 encoding of an image
def get_image_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# Function to analyze image with Groq API
def analyze_image(
    image_url=None,
    image_base64=None,
    prompt="Describe what you see in this image in detail.",
):
    # Prepare the message with the image
    if image_url:
        image_content = {"type": "image_url", "image_url": {"url": image_url}}
    elif image_base64:
        image_content = {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
        }
    else:
        return "No image provided"

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an image analysis assistant. Provide detailed and accurate descriptions of images.",
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}, image_content],
                },
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            temperature=0.5,
            max_completion_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing image: {str(e)}"


# Create tabs for different input methods
tab1, tab2 = st.tabs(["Upload Image", "Image URL"])

with tab1:
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        # Convert image to base64
        image_base64 = get_image_base64(image)

        # Analysis prompt
        user_prompt = st.text_input(
            "What would you like to know about this image?",
            "Describe what you see in this image in detail.",
            key="upload_prompt",
        )

        # Analyze button
        if st.button("Analyze Image", key="analyze_upload"):
            with st.spinner("Analyzing image..."):
                analysis = analyze_image(image_base64=image_base64, prompt=user_prompt)

                # Display results
                st.subheader("Analysis Results")
                st.write(analysis)

with tab2:
    url = st.text_input("Enter the URL of an image")

    if url:
        try:
            # Validate and display the image from URL
            response = requests.get(url)
            image = Image.open(io.BytesIO(response.content))
            st.image(image, caption="Image from URL", use_container_width=True)

            # Analysis prompt
            user_prompt = st.text_input(
                "What would you like to know about this image?",
                "Describe what you see in this image in detail.",
                key="url_prompt",
            )

            # Analyze button
            if st.button("Analyze Image", key="analyze_url"):
                with st.spinner("Analyzing image..."):
                    analysis = analyze_image(image_url=url, prompt=user_prompt)

                    # Display results
                    st.subheader("Analysis Results")
                    st.write(analysis)
        except Exception as e:
            st.error(f"Error loading image from URL: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Powered by Groq API and Streamlit")

# # API Key configuration section
# with st.expander("API Configuration"):
#     st.write("The app requires a Groq API key to function.")

#     if not api_key:
#         st.warning(
#             "API Key not found in environment variables. Please set it below or in a .env file."
#         )

#     new_api_key = st.text_input(
#         "Groq API Key", value=api_key if api_key else "", type="password"
#     )

#     if st.button("Save API Key"):
#         # This is just for session-based usage, in a real app you would save this more securely
#         if new_api_key:
#             # Create/update .env file
#             with open(".env", "w") as f:
#                 f.write(f"API_KEY={new_api_key}")
#             st.success(
#                 "API Key saved! Please restart the app for changes to take effect."
#             )
#             # Update the client with new key
#             client = Groq(api_key=new_api_key)
#         else:
#             st.error("Please enter a valid API key.")
