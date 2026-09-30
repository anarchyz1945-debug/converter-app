import io
import re
import base64
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import cairosvg

# Hilangkan limit deteksi bom kompresi gambar
Image.MAX_IMAGE_PIXELS = None

st.set_page_config(
    page_title="Microstock File Converter",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Microstock Multi-Converter")
st.caption("Konversi SVG & PNG siap upload ke Shutterstock, Adobe Stock, dan Magnific/Freepik")

def pad_eps_file(eps_bytes, target_min_bytes=600 * 1024):
    current_size = len(eps_bytes)
    if current_size < target_min_bytes:
        needed_bytes = target_min_bytes - current_size
        padding = b"\n% Microstock size padding\n" + (b"% " + b"0" * 60 + b"\n") * (needed_bytes // 63)
        return eps_bytes + padding
    return eps_bytes

def fix_and_render_svg_preview(svg_bytes):
    # Bersihkan / normalkan isi SVG agar aman dibaca CairoSVG
    svg_text = svg_bytes.decode("utf-8", errors="ignore")
    
    # Jika tidak ada viewBox tetapi ada width dan height, buatkan viewBox
    if "viewBox" not in svg_text:
        w_match = re.search(r'width=["\']([0-9.]+)', svg_text)
        h_match = re.search(r'height=["\']([0-9.]+)', svg_text)
        if w_match and h_match:
            w, h = w_match.group(1), h_match.group(1)
            svg_text = re.sub(r'<svg', f'<svg viewBox="0 0 {w} {h}"', svg_text, count=1)
        else:
            # Fallback default viewBox standar
            svg_text = re.sub(r'<svg', '<svg viewBox="0 0 1000 1000"', svg_text, count=1)
    
    clean_bytes = svg_text.encode("utf-8")
    
    # Render PNG preview dengan batas ukuran aman (maksimal 2000px)
    png_data = cairosvg.svg2png(bytestring=clean_bytes, output_width=2000)
    
    img = Image.open(io.BytesIO(png_data))
    
    # Konversi RGBA ke RGB berlatar belakang putih
    if img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if "A" in img.mode:
            bg.paste(img, mask=img.split()[-1])
        else:
            bg.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
        
    jpg_buf = io.BytesIO()
    img.save(jpg_buf, format="JPEG", quality=92)
    return clean_bytes, jpg_buf.getvalue()

tab_mag, tab_svg, tab_png = st.tabs([
    "⭐ SVG ke EPS + JPG (Khusus Magnific)", 
    "📐 SVG ke EPS Standar", 
    "🖼️ PNG ke JPG"
])

# ==========================================================
# TAB 1: KHUSUS MAGNIFIC / FREEPIK
# ==========================================================
with tab_mag:
    st.subheader("Konversi SVG ➔ EPS (>500KB) + JPG Preview")
    uploaded_mag_svgs = st.file_uploader(
        "Pilih file SVG (bisa pilih banyak)",
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
                raw_svg = file.getvalue()
                clean_svg_bytes, jpg_bytes = fix_and_render_svg_preview(raw_svg)

                # Konversi ke EPS lalu pad di atas 500 KB
                raw_eps = cairosvg.svg2eps(bytestring=clean_svg_bytes)
                padded_eps = pad_eps_file(raw_eps, target_min_bytes=600 * 1024)
                
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
# TAB 2: SVG KE EPS STANDAR (SHUTTERSTOCK / ADOBE STOCK)
# ==========================================================
with tab_svg:
    st.subheader("Konversi SVG ke EPS Standar")
    uploaded_svgs = st.file_uploader(
        "Pilih file SVG (bisa pilih banyak)",
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
# TAB 3: PNG KE JPG
# ==========================================================
with tab_png:
    st.subheader("Konversi PNG ke JPG")
    uploaded_pngs = st.file_uploader(
        "Pilih gambar PNG (bisa pilih banyak)", 
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
