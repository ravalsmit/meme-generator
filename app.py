import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap, io, zipfile

# ---- UI CONFIG ----
st.set_page_config(page_title="Bulk Meme Generator", layout="centered")

# Bigger mobile title
st.markdown("""
<h1 style="text-align:center; font-size:36px; margin-bottom:10px;">
🔥 Bulk 5:6 Meme Generator
</h1>
<p style="text-align:center; font-size:18px; opacity:0.7;">
Upload many images + a text file with captions
</p>
""", unsafe_allow_html=True)

# Better spacing
st.write("")

# ---- Upload UI ----
uploaded_images = st.file_uploader(
    "Images (JPG/PNG)", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

uploaded_text = st.file_uploader(
    "Captions File (.txt — one caption per line)",
    type=["txt"]
)

st.write("")
generate = st.button("🚀 Generate Memes", use_container_width=True)
st.write("")

# ---- Meme Function ----
def create_meme(img, text):
    final_w = 1080
    final_h = int(final_w * (6/5))
    text_ratio = 0.35
    text_h = int(final_h * text_ratio)
    img_h = final_h - text_h

    canvas = Image.new("RGB", (final_w, final_h), "white")
    text_box = Image.new("RGB", (final_w, text_h), "white")
    draw = ImageDraw.Draw(text_box)

    # Mobile-friendly bigger text
    try: font = ImageFont.truetype("arialbd.ttf", 70)
    except: font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=22)
    line_h = font.getbbox("A")[3]
    total_h = len(lines)*(line_h+10)
    y = (text_h-total_h)//2

    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        w = bbox[2]-bbox[0]
        h = bbox[3]-bbox[1]
        x = (final_w-w)//2
        draw.text((x,y), line, font=font, fill="black")
        y += h+12

    canvas.paste(text_box, (0,0))

    ow, oh = img.size
    scale = max(final_w/ow, img_h/oh)
    nw, nh = int(ow*scale), int(oh*scale)
    img_r = img.resize((nw, nh), Image.LANCZOS)
    left = (nw-final_w)//2
    top = (nh-img_h)//2
    img_c = img_r.crop((left, top, left+final_w, top+img_h))
    canvas.paste(img_c, (0, text_h))

    return canvas

# ---- Generate ----
if generate:
    if not uploaded_images or not uploaded_text:
        st.warning("Please upload images and a text file first.")
    else:
        captions = uploaded_text.read().decode("utf-8").splitlines()
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as z:
            for idx, img_file in enumerate(uploaded_images):
                if idx >= len(captions): break
                img = Image.open(img_file)
                meme = create_meme(img, captions[idx])

                memfile = io.BytesIO()
                meme.save(memfile, format="JPEG", quality=95)
                memfile.seek(0)

                z.writestr(f"meme_{idx+1}.jpg", memfile.read())

        st.success("✅ Memes ready!")
        st.download_button(
            "⬇️ Download All Memes",
            data=zip_buffer.getvalue(),
            file_name="memes.zip",
            use_container_width=True,
            mime="application/zip"
        )

# UI Footer
st.write("")
st.caption("Tip: Use 1080×1296 images for best output")
