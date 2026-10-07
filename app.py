import io
import re
import base64
import zipfile
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import cairosvg

Image.MAX_IMAGE_PIXELS = None

st.set_page_config(
    page_title="Microstock Multi-Converter",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Microstock Multi-Converter")
st.caption("Konversi SVG & PNG siap untuk Shutterstock, Adobe Stock, Magnific, dan Pngtree")

def pad_eps_file(eps_bytes, target_min_bytes=600 * 1024):
    current_size = len(eps_bytes)
    if current_size < target_min_bytes:
        needed_bytes = target_min_bytes - current_size
        padding = b"\n% Microstock size padding\n" + (b"% " + b"0" * 60 + b"\n") * (needed_bytes // 63)
        return eps_bytes + padding
    return eps_bytes

def clean_svg_string(svg_bytes):
    svg_text = svg_bytes.decode("utf-8", errors="ignore")
    if "viewBox" not in svg_text:
        w_match = re.search(r'width=["\']([0-9.]+)', svg_text)
        h_match = re.search(r'height=["\']([0-9.]+)', svg_text)
        if w_match and h_match:
            w, h = w_match.group(1), h_match.group(1)
            svg_text = re.sub(r'<svg', f'<svg viewBox="0 0 {w} {h}"', svg_text, count=1)
        else:
            svg_text = re.sub(r'<svg', '<svg viewBox="0 0 5000 5000"', svg_text, count=1)
    return svg_text.encode("utf-8")

# Generator PNG Pngtree: Full Size 5000x5000 px (Transparan Resolusi Tinggi)
def generate_pngtree_fullsize_png(clean_svg_bytes):
    # Render langsung ke ukuran asli 5000x5000 px
    png_data = cairosvg.svg2png(
        bytestring=clean_svg_bytes, 
        output_width=5000, 
        output_height=5000
    )
    return png_data

# Generator Preview Magnific (JPG Latar Putih)
def generate_magnific_jpg(clean_svg_bytes):
    raw_png = cairosvg.svg2png(bytestring=clean_svg_bytes, output_width=2500)
    img = Image.open(io.BytesIO(raw_png))
    if img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if "A" in img.mode:
            bg.paste(img, mask=img.split()[-1])
        else:
            bg.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

tab_mag, tab_pngtree, tab_svg, tab_png = st.tabs([
    "⭐ Magnific (EPS + JPG Lepas)", 
    "🌳 Pngtree (Auto-ZIP EPS+PNG 5000px)",
    "📐 SVG ke EPS Standar", 
    "🖼️ PNG ke JPG"
])

# ==========================================================
# TAB 1: KHUSUS MAGNIFIC
# ==========================================================
with tab_mag:
    st.subheader("Konversi SVG ➔ EPS (>500KB) + JPG Preview")
    uploaded_mag_svgs = st.file_uploader(
        "Pilih file SVG (bisa banyak)",
        type=["svg"],
        accept_multiple_files=True,
        key="uploader_mag_svg"
    )

    if uploaded_mag_svgs:
        st.write(f"📁 Terpilih: **{len(uploaded_mag_svgs)} file**")
        st.markdown("---")

        for idx, file in enumerate(uploaded_mag_svgs):
            base_name = file.name.rsplit(".", 1)[0]
            eps_name = f"{base_name}.eps"
            jpg_name = f"{base_name}.jpg"

            try:
                clean_svg = clean_svg_string(file.getvalue())
                raw_eps = cairosvg.svg2eps(bytestring=clean_svg)
                padded_eps = pad_eps_file(raw_eps, target_min_bytes=600 * 1024)
                jpg_bytes = generate_magnific_jpg(clean_svg)
                
                b64_eps = base64.b64encode(padded_eps).decode()
                b64_jpg = base64.b64encode(jpg_bytes).decode()
                size_kb = round(len(padded_eps) / 1024)

                col1, col2 = st.columns([3, 3])
                with col1:
                    st.write(f"📦 **{base_name}** (`{size_kb} KB`)")
                with col2:
                    btn_html = f"""
                    <div style="display: flex; gap: 8px;">
                        <a href="data:application/postscript;base64,{b64_eps}" download="{eps_name}" style="text-decoration: none;">
                            <button style="background-color: #0088cc; color: white; border: none; padding: 7px 12px; border-radius: 6px; font-weight: 500; font-size: 13px; cursor: pointer;">
                                ⬇️ EPS
                            </button>
                        </a>
                        <a href="data:image/jpeg;base64,{b64_jpg}" download="{jpg_name}" style="text-decoration: none;">
                            <button style="background-color: #FF4B4B; color: white; border: none; padding: 7px 12px; border-radius: 6px; font-weight: 500; font-size: 13px; cursor: pointer;">
                                ⬇️ JPG Preview
                            </button>
                        </a>
                    </div>
                    """
                    components.html(btn_html, height=45)
            except Exception as e:
                st.error(f"Gagal memproses {file.name}: {e}")

# ==========================================================
# TAB 2: KHUSUS PNGTREE (ZIP: EPS + PNG FULL 5000x5000 PX)
# ==========================================================
with tab_pngtree:
    st.subheader("Konversi SVG ➔ Paket ZIP Pngtree (EPS + PNG 5000px)")
    st.caption("Otomatis membungkus EPS dan file PNG transparan 5000x5000 px ke dalam satu file .ZIP.")
    
    uploaded_pngtree_svgs = st.file_uploader(
        "Pilih file SVG untuk Pngtree (bisa banyak)",
        type=["svg"],
        accept_multiple_files=True,
        key="uploader_pngtree_svg"
    )

    if uploaded_pngtree_svgs:
        st.write(f"📁 Terpilih: **{len(uploaded_pngtree_svgs)} file**")
        st.markdown("---")

        for idx, file in enumerate(uploaded_pngtree_svgs):
            base_name = file.name.rsplit(".", 1)[0]
            zip_filename = f"{base_name}.zip"

            try:
                clean_svg = clean_svg_string(file.getvalue())
                eps_bytes = cairosvg.svg2eps(bytestring=clean_svg)
                png_bytes = generate_pngtree_fullsize_png(clean_svg)

                # Masukkan EPS dan PNG ke dalam ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr(f"{base_name}.eps", eps_bytes)
                    zf.writestr(f"{base_name}.png", png_bytes)

                zip_data = zip_buffer.getvalue()
                zip_size_kb = round(len(zip_data) / 1024)
                b64_zip = base64.b64encode(zip_data).decode()

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"📁 **{zip_filename}** (`{zip_size_kb} KB`)")
                with col2:
                    btn_zip_html = f"""
                    <a href="data:application/zip;base64,{b64_zip}" download="{zip_filename}" style="text-decoration: none;">
                        <button style="background-color: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 500; font-size: 13px; cursor: pointer;">
                            ⬇️ Download ZIP
                        </button>
                    </a>
                    """
                    components.html(btn_zip_html, height=45)
            except Exception as e:
                st.error(f"Gagal memproses {file.name}: {e}")

# ==========================================================
# TAB 3: SVG KE EPS STANDAR
# ==========================================================
with tab_svg:
    st.subheader("Konversi SVG ke EPS Standar")
    uploaded_svgs = st.file_uploader(
        "Pilih file SVG (bisa banyak)",
        type=["svg"],
        accept_multiple_files=True,
        key="uploader_svg_batch"
    )

    if uploaded_svgs:
        st.write(f"📁 Terpilih: **{len(uploaded_svgs)} file**")
        st.markdown("---")

        for idx, file in enumerate(uploaded_svgs):
            base_name_svg = file.name.rsplit(".", 1)[0]
            eps_filename = f"{base_name_svg}.eps"

            try:
                svg_bytes = file.getvalue()
                eps_data = cairosvg.svg2eps(bytestring=svg_bytes)
                b64_eps = base64.b64encode(eps_data).decode()

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"📐 **{eps_filename}**")
                with col2:
                    html_eps_button = f"""
                    <a href="data:application/postscript;base64,{b64_eps}" download="{eps_filename}" style="text-decoration: none;">
                        <button style="background-color: #FF4B4B; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 500; font-size: 14px; cursor: pointer;">
                            ⬇️ Unduh EPS
                        </button>
                    </a>
                    """
                    components.html(html_eps_button, height=45)
            except Exception as e:
                st.error(f"Gagal mengonversi {file.name}: {e}")

# ==========================================================
# TAB 4: PNG KE JPG
# ==========================================================
with tab_png:
    st.subheader("Konversi PNG ke JPG")
    uploaded_pngs = st.file_uploader(
        "Pilih gambar PNG (bisa banyak)", 
        type=["png"], 
        accept_multiple_files=True,
        key="uploader_png_batch"
    )

    if uploaded_pngs:
        st.write(f"📁 Terpilih: **{len(uploaded_pngs)} file**")
        st.markdown("---")

        for idx, file in enumerate(uploaded_pngs):
            base_name_png = file.name.rsplit(".", 1)[0]
            jpg_filename = f"{base_name_png}.jpg"

            try:
                image = Image.open(file)
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                
                jpg_buffer = io.BytesIO()
                image.save(jpg_buffer, format="JPEG", quality=100, subsampling=0)
                jpg_bytes = jpg_buffer.getvalue()
                b64_jpg = base64.b64encode(jpg_bytes).decode()

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"🖼️ **{jpg_filename}**")
                with col2:
                    html_jpg_button = f"""
                    <a href="data:image/jpeg;base64,{b64_jpg}" download="{jpg_filename}" style="text-decoration: none;">
                        <button style="background-color: #FF4B4B; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 500; font-size: 14px; cursor: pointer;">
                            ⬇️ Unduh JPG
                        </button>
                    </a>
                    """
                    components.html(html_jpg_button, height=45)
            except Exception as e:
                st.error(f"Gagal mengonversi {file.name}: {e}") 
