import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap, io, zipfile

st.set_page_config(page_title="Bulk Meme Generator", layout="centered")
st.title("🔥 Bulk 5:6 Meme Generator — Mobile Friendly")

# Upload section
uploaded_images = st.file_uploader(
    "📸 Upload Images", type=["jpg","jpeg","png"], accept_multiple_files=True
)
uploaded_text = st.file_uploader(
    "📝 Upload Text File (one caption per line)", type=["txt"]
)

generate = st.button("🚀 Generate Memes")

# ======================================
# Meme creation function (dynamic font)
# ======================================
def create_meme(img, text):
    final_w = 1080
    final_h = int(final_w * (6/5))
    text_ratio = 0.35
    text_h = int(final_h * text_ratio)
    img_h = final_h - text_h

    canvas = Image.new("RGB", (final_w, final_h), "white")

    # --- Auto font scaling based on text box height ---
    base_font_size = int(text_h * 0.10) + 30  # +30 boost
    min_font = 80  # raise minimum to keep text bold on mobile
    font_size = max(base_font_size, min_font)
    
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()

    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # --- Text box setup ---
    text_box = Image.new("RGB", (final_w, text_h), "white")
    draw = ImageDraw.Draw(text_box)

    wrap_chars = max(15, int(900 // font_size))
    lines = textwrap.wrap(text, width=wrap_chars)

    line_h = font.getbbox("A")[3]
    total_h = len(lines) * (line_h + 10)
    y = (text_h - total_h) // 2

    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (final_w - w) // 2
        draw.text((x, y), line, font=font, fill="black")
        y += h + 10

    canvas.paste(text_box, (0,0))

    # --- Image center crop ---
    img = img.convert("RGB")
    ow, oh = img.size
    scale = max(final_w/ow, img_h/oh)
    nw, nh = int(ow*scale), int(oh*scale)
    img_r = img.resize((nw, nh), Image.LANCZOS)

    l = (nw-final_w)//2
    t = (nh-img_h)//2
    img_c = img_r.crop((l, t, l+final_w, t+img_h))

    canvas.paste(img_c, (0, text_h))
    return canvas

# ======================================
# Generate Results
# ======================================
if generate and uploaded_images and uploaded_text:
    captions = uploaded_text.read().decode("utf-8").splitlines()
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as z:
        for idx, img_file in enumerate(uploaded_images):
            if idx >= len(captions): break
            img = Image.open(img_file)
            meme = create_meme(img, captions[idx])

            img_bytes = io.BytesIO()
            meme.save(img_bytes, format="JPEG", quality=95)
            img_bytes.seek(0)

            z.writestr(f"meme_{idx+1}.jpg", img_bytes.read())

    st.success("✅ Bulk memes ready!")
    st.download_button(
        "⬇️ Download Pack (.zip)",
        data=zip_buffer.getvalue(),
        file_name="memes.zip",
        mime="application/zip"
    )
else:
    st.caption("Upload images + text, then hit Generate ✅")

