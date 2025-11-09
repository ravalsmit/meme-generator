import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap, io, zipfile, os

st.set_page_config(page_title="⚡️ Vertical Meme Studio (5:6)", layout="centered")
st.title("⚡️ Vertical Meme Studio (5:6)")
st.write("Create memes in bulk — paste text or upload a .txt file (one caption per line).")

# --- Inputs ---
uploaded_images = st.file_uploader(
    "Upload Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

captions_input = st.text_area(
    "Paste Captions Here (one per line)",
    placeholder="When life gives you lemons...\nSecond caption here...",
    height=150
)

uploaded_text = st.file_uploader(
    "Or Upload Caption File (.txt)",
    type=["txt"]
)

generate = st.button("Generate Memes")


def create_meme(img, text):
    # Canvas 5:6 ratio
    final_w = 1080
    final_h = int(final_w * (6/5))
    text_ratio = 0.35
    text_h = int(final_h * text_ratio)
    img_h = final_h - text_h

    canvas = Image.new("RGB", (final_w, final_h), "white")

    # Text area
    text_box = Image.new("RGB", (final_w, text_h), "white")
    draw = ImageDraw.Draw(text_box)

    font_path = os.path.join("fonts", "arialbd.ttf")
    try:
        font = ImageFont.truetype(font_path, 60)
    except:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=25)
    line_h = font.getbbox("A")[3]
    total_h = len(lines)*(line_h+10)
    y = (text_h-total_h)//2

    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        w = bbox[2]-bbox[0]
        h = bbox[3]-bbox[1]
        x = (final_w-w)//2
        draw.text((x,y), line, font=font, fill="black")
        y += h+10

    canvas.paste(text_box, (0,0))

    # Fit & crop image
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


if generate and uploaded_images:
    # Pick captions source
    if uploaded_text:
        captions = uploaded_text.read().decode("utf-8").splitlines()
    else:
        captions = captions_input.splitlines()

    captions = [c.strip() for c in captions if c.strip()]

    if not captions:
        st.warning("Please provide captions — paste or upload a .txt.")
    else:
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

        st.success("✅ Memes Generated!")
        st.download_button(
            "⬇️ Download Zip",
            data=zip_buffer.getvalue(),
            file_name="memes.zip",
            mime="application/zip"
        )
else:
    st.caption("Upload images and provide captions to generate memes.")
