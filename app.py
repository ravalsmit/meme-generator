import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap, io, zipfile, os, requests

st.set_page_config(page_title="Bulk Meme Generator", layout="centered")
st.title("🧠 Bulk 5:6 Meme Generator")

# --- Constants ---
GOOGLE_FONTS = {
    "Anton (Impact-like)":   "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",
    "Oswald (Condensed)":    "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald[wght].ttf",
    "Roboto (Clean)":        "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto[wdth,wght].ttf",
    "Montserrat (Modern)":   "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat[wght].ttf",
    "Poppins (Rounded)":     "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf"
}

# --- Sidebar Settings ---
st.sidebar.header("🎨 Styling Options")
bg_color = st.sidebar.color_picker("Background Color", "#FFFFFF")
text_color = st.sidebar.color_picker("Text Color", "#000000")
font_choice = st.sidebar.selectbox("Choose Font", list(GOOGLE_FONTS.keys()))
font_size = st.sidebar.slider("Font Size", 30, 100, 60)

# Uploads
uploaded_images = st.file_uploader("Upload Images", type=["jpg","jpeg","png"], accept_multiple_files=True)
uploaded_text = st.file_uploader("Upload Text File (one caption per line)", type=["txt"])

generate = st.button("Generate Memes")

@st.cache_resource
def load_font(font_name, size):
    """Fetches font from URL and returns ImageFont object."""
    url = GOOGLE_FONTS[font_name]
    try:
        response = requests.get(url)
        response.raise_for_status()
        return ImageFont.truetype(io.BytesIO(response.content), size)
    except Exception as e:
        st.error(f"Failed to load font {font_name}: {e}")
        return ImageFont.load_default()

def create_meme(img, text, bg_col, txt_col, f_size, font_name):
    # --- Canvas 5:6 ratio ---
    final_w = 1080
    final_h = int(final_w * (6/5))
    text_ratio = 0.35
    text_h = int(final_h * text_ratio)
    img_h = final_h - text_h

    canvas = Image.new("RGB", (final_w, final_h), bg_col)

    # --- Text box ---
    text_box = Image.new("RGB", (final_w, text_h), bg_col)
    draw = ImageDraw.Draw(text_box)

    # --- Font Loading ---
    font = load_font(font_name, f_size)

    # --- Text Wrapping & Rendering ---
    # Estimate chars per line based on width (rough approx)
    avg_char_width = f_size * 0.5 
    chars_per_line = int((final_w - 40) / avg_char_width) # 40px padding
    lines = textwrap.wrap(text, width=chars_per_line)

    # Calculate total text height
    try:
        ascent, descent = font.getmetrics()
        line_h = ascent + descent
    except:
        # Fallback for default font which might not have getmetrics
        line_h = f_size * 1.2

    total_h = len(lines) * (line_h + 10)
    y = (text_h - total_h) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (final_w - w) // 2
        draw.text((x, y), line, font=font, fill=txt_col)
        y += line_h + 10

    canvas.paste(text_box, (0, 0))

    # --- Image crop fill ---
    try:
        img = img.convert("RGB")
        ow, oh = img.size
        scale = max(final_w / ow, img_h / oh)
        nw, nh = int(ow * scale), int(oh * scale)
        img_r = img.resize((nw, nh), Image.LANCZOS)

        l = (nw - final_w) // 2
        t = (nh - img_h) // 2

        img_c = img_r.crop((l, t, l + final_w, t + img_h))
        canvas.paste(img_c, (0, text_h))
    except Exception as e:
        print(f"Error processing image: {e}")
        pass

    return canvas

if generate and uploaded_images and uploaded_text:
    captions = uploaded_text.read().decode("utf-8").splitlines()
    zip_buffer = io.BytesIO()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    processed_count = 0

    with zipfile.ZipFile(zip_buffer, "w") as z:
        for idx, img_file in enumerate(uploaded_images):
            if idx >= len(captions): 
                break
            
            try:
                img = Image.open(img_file)
                meme = create_meme(img, captions[idx], bg_color, text_color, font_size, font_choice)

                img_bytes = io.BytesIO()
                meme.save(img_bytes, format="JPEG", quality=95)
                img_bytes.seek(0)

                z.writestr(f"meme_{idx+1}.jpg", img_bytes.read())
                processed_count += 1
            except Exception as e:
                st.error(f"Failed to process image {img_file.name}: {e}")
            
            # Update progress
            progress_bar.progress((idx + 1) / len(uploaded_images))

    status_text.success(f"✅ Generated {processed_count} Memes!")
    st.download_button("⬇️ Download Zip", data=zip_buffer.getvalue(), file_name="memes.zip", mime="application/zip")
elif generate:
    st.warning("⚠️ Please upload both images and a text file.")
else:
    st.caption("Upload files & click Generate")
