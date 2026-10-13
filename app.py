import io
import re
import zipfile
import gc
import streamlit as st
from PIL import Image

# Penanganan impor CairoSVG
try:
    import cairosvg
except Exception:
    cairosvg = None

# Bebaskan batasan piksel Pillow
Image.MAX_IMAGE_PIXELS = None

st.set_page_config(
    page_title="Microstock Multi-Converter",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Microstock Multi-Converter")
st.caption("Konversi SVG & PNG siap untuk Shutterstock, Adobe Stock, Magnific, Pngtree, dan Pond5")

if cairosvg is None:
    st.error("Gagal memuat CairoSVG. Silakan periksa file packages.txt pada repositori GitHub.")
    st.stop()

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

# Render hemat RAM (Render 2000px -> Upscale Lanczos 5000px)
def generate_jpg_preview(clean_svg_bytes, target_dim=5000):
    raw_png = cairosvg.svg2png(bytestring=clean_svg_bytes, output_width=2000, output_height=2000)
    img = Image.open(io.BytesIO(raw_png))
    
    if img.size != (target_dim, target_dim):
        resample_filter = getattr(Image.Resampling, 'LANCZOS', Image.LANCZOS)
        img = img.resize((target_dim, target_dim), resample=resample_filter)
        
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
    del raw_png
    gc.collect()
    return buf.getvalue()

def generate_pngtree_fullsize_png(clean_svg_bytes):
    raw_png = cairosvg.svg2png(bytestring=clean_svg_bytes, output_width=2500, output_height=2500)
    img = Image.open(io.BytesIO(raw_png))
    if img.size != (5000, 5000):
        resample_filter = getattr(Image.Resampling, 'LANCZOS', Image.LANCZOS)
        img = img.resize((5000, 5000), resample=resample_filter)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    del raw_png
    gc.collect()
    return buf.getvalue()

tab_mag, tab_pond5, tab_pngtree, tab_svg, tab_png = st.tabs([
    "⭐ Magnific (EPS + JPG Lepas)", 
    "🌊 Pond5 (Auto-ZIP EPS+JPG 5000px)",
    "🌳 Pngtree (Auto-ZIP EPS+PNG 5000px)",
    "📐 SVG ke EPS Standar", 
    "🖼️ PNG ke JPG"
])

# TAB 1: MAGNIFIC / FREEPIK
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
                jpg_bytes = generate_jpg_preview(clean_svg, target_dim=5000)
                size_kb = round(len(padded_eps) / 1024)

                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"📦 **{base_name}** (`{size_kb} KB`)")
                with col2:
                    st.download_button(
                        label="⬇️ Unduh EPS",
                        data=padded_eps,
                        file_name=eps_name,
                        mime="application/postscript",
                        key=f"dl_eps_{idx}"
                    )
                with col3:
                    st.download_button(
                        label="⬇️ JPG Preview",
                        data=jpg_bytes,
                        file_name=jpg_name,
                        mime="image/jpeg",
                        key=f"dl_jpg_{idx}"
                    )
            except Exception as e:
                st.error(f"Gagal memproses {file.name}: {e}")

# TAB 2: POND5
with tab_pond5:
    st.subheader("Konversi SVG ➔ Paket ZIP Pond5 (EPS + JPG 5000px)")
    st.caption("Otomatis membungkus EPS dan JPEG thumbnail (5000x5000 px) ke dalam satu file .ZIP siap upload ke Pond5.")
    
    uploaded_pond5_svgs = st.file_uploader(
        "Pilih file SVG untuk Pond5 (bisa banyak)",
        type=["svg"],
        accept_multiple_files=True,
        key="uploader_pond5_svg"
    )

    if uploaded_pond5_svgs:
        st.write(f"📁 Terpilih: **{len(uploaded_pond5_svgs)} file**")
        st.markdown("---")

        for idx, file in enumerate(uploaded_pond5_svgs):
            base_name = file.name.rsplit(".", 1)[0].replace(" ", "_")
            zip_filename = f"{base_name}.zip"

            try:
                clean_svg = clean_svg_string(file.getvalue())
                eps_bytes = cairosvg.svg2eps(bytestring=clean_svg)
                jpg_bytes = generate_jpg_preview(clean_svg, target_dim=5000)

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr(f"{base_name}.eps", eps_bytes)
                    zf.writestr(f"{base_name}.jpg", jpg_bytes)

                zip_data = zip_buffer.getvalue()
                zip_size_kb = round(len(zip_data) / 1024)

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"📁 **{zip_filename}** (`{zip_size_kb} KB`)")
                with col2:
                    st.download_button(
                        label="⬇️ Download ZIP Pond5",
                        data=zip_data,
                        file_name=zip_filename,
                        mime="application/zip",
                        key=f"dl_pond5_{idx}"
                    )
            except Exception as e:
                st.error(f"Gagal memproses {file.name}: {e}")

# TAB 3: PNGTREE
with tab_pngtree:
    st.subheader("Konversi SVG ➔ Paket ZIP Pngtree (EPS + PNG 5000px)")
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

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr(f"{base_name}.eps", eps_bytes)
                    zf.writestr(f"{base_name}.png", png_bytes)

                zip_data = zip_buffer.getvalue()
                zip_size_kb = round(len(zip_data) / 1024)

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"📁 **{zip_filename}** (`{zip_size_kb} KB`)")
                with col2:
                    st.download_button(
                        label="⬇️ Download ZIP",
                        data=zip_data,
                        file_name=zip_filename,
                        mime="application/zip",
                        key=f"dl_pngtree_{idx}"
                    )
            except Exception as e:
                st.error(f"Gagal memproses {file.name}: {e}")

# TAB 4: SVG KE EPS STANDAR
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

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"📐 **{eps_filename}**")
                with col2:
                    st.download_button(
                        label="⬇️ Unduh EPS",
                        data=eps_data,
                        file_name=eps_filename,
                        mime="application/postscript",
                        key=f"dl_std_eps_{idx}"
                    )
            except Exception as e:
                st.error(f"Gagal mengonversi {file.name}: {e}")

# TAB 5: PNG KE JPG
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

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"🖼️ **{jpg_filename}**")
                with col2:
                    st.download_button(
                        label="⬇️ Unduh JPG",
                        data=jpg_bytes,
                        file_name=jpg_filename,
                        mime="image/jpeg",
                        key=f"dl_std_jpg_{idx}"
                    )
            except Exception as e:
                st.error(f"Gagal mengonversi {file.name}: {e}") 
