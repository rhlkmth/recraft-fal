# app.py
import streamlit as st
import os
import fal_client
from PIL import Image
import requests
from io import BytesIO
import time

# Page config
st.set_page_config(page_title="AI Image Generator", page_icon="🎨")

# Title
st.title("🎨 AI Image Generator")

# Initialize session state for generated images
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

# Sidebar for API key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter your FAL API key", type="password")
    if api_key:
        os.environ["FAL_KEY"] = api_key

# Main interface
prompt = st.text_area("Enter your prompt:", height=100, placeholder="A wildlife photography photo of a red panda using a laptop in a snowy forest")

# Style selection
styles = [
    "any", "realistic_image", "digital_illustration", "digital_illustration/pixel_art",
    "digital_illustration/hand_drawn", "digital_illustration/grain",
    "digital_illustration/infantile_sketch", "digital_illustration/2d_art_poster",
    "digital_illustration/handmade_3d", "digital_illustration/hand_drawn_outline",
    "digital_illustration/engraving_color", "digital_illustration/2d_art_poster_2",
    "realistic_image/b_and_w", "realistic_image/hard_flash", "realistic_image/hdr",
    "realistic_image/natural_light", "realistic_image/studio_portrait",
    "realistic_image/enterprise", "realistic_image/motion_blur"
]

style = st.selectbox("Select style:", styles)

# Size selection
sizes = {
    "1024x1024": {"width": 1024, "height": 1024},
    "1365x1024": {"width": 1365, "height": 1024},
    "1024x1365": {"width": 1024, "height": 1365},
    "1536x1024": {"width": 1536, "height": 1024},
    "1024x1536": {"width": 1024, "height": 1536}
}

size = st.selectbox("Select size:", list(sizes.keys()))

# Generate button
if st.button("Generate Image"):
    if not api_key:
        st.error("Please enter your FAL API key in the sidebar.")
    elif not prompt:
        st.error("Please enter a prompt.")
    else:
        try:
            with st.spinner("Generating image... This may take a few moments."):
                # Submit request to the API
                result = fal_client.subscribe(
                    "fal-ai/recraft-v3",
                    arguments={
                        "prompt": prompt,
                        "image_size": sizes[size],
                        "style": style,
                        "enable_safety_checker": False,
                    }
                )

                # Process the result
                if result and result["images"]:
                    img_url = result["images"][0]["url"]
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        # Add to session state
                        st.session_state.generated_images.append({
                            "image": image,
                            "prompt": prompt,
                            "style": style,
                            "size": size,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.success("Image generated successfully!")
                    else:
                        st.error("Failed to download the generated image.")
                else:
                    st.error("No output received from the model.")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display generated images
if st.session_state.generated_images:
    st.header("Generated Images")
    for idx, img_data in enumerate(reversed(st.session_state.generated_images)):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(img_data["image"], use_column_width=True)
        with col2:
            st.write("**Prompt:**", img_data["prompt"])
            st.write("**Style:**", img_data["style"])
            st.write("**Size:**", img_data["size"])
            st.write("**Generated at:**", img_data["timestamp"])
        st.divider()

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and FAL API")
