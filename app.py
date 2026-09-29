import io
import base64
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import cairosvg

st.set_page_config(
    page_title="Vector & Image Converter",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 File Converter")
st.caption("Konversi SVG ➔ EPS & PNG ➔ JPG — Multi-upload tanpa refresh halaman")

tab_svg, tab_png = st.tabs(["📐 SVG ke EPS", "🖼️ PNG ke JPG"])

# ==========================================
# TAB 1: SVG KE EPS (MULTI-UPLOAD & ANTI-REFRESH)
# ==========================================
with tab_svg:
    st.subheader("Konversi SVG ke EPS")
    uploaded_svgs = st.file_uploader(
        "Pilih file SVG (bisa pilih banyak sekaligus)",
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
                # Konversi vektor murni dengan cairosvg
                svg_bytes = file.getvalue()
                eps_data = cairosvg.svg2eps(bytestring=svg_bytes)
                b64_eps = base64.b64encode(eps_data).decode()

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"📐 **{eps_filename}**")
                with col2:
                    # Tombol download HTML instan (bebas refresh)
                    html_eps_button = f"""
                    <a href="data:application/postscript;base64,{b64_eps}" download="{eps_filename}" style="text-decoration: none;">
                        <button style="
                            background-color: #FF4B4B;
                            color: white;
                            border: none;
                            padding: 8px 16px;
                            border-radius: 6px;
                            font-weight: 500;
                            font-size: 14px;
                            cursor: pointer;
                            display: inline-flex;
                            align-items: center;
                            gap: 5px;
                        ">
                            ⬇️ Unduh EPS
                        </button>
                    </a>
                    """
                    components.html(html_eps_button, height=45)

            except Exception as e:
                st.error(f"Gagal mengonversi {file.name}: {e}")

# ==========================================
# TAB 2: PNG KE JPG (MULTI-UPLOAD & ANTI-REFRESH)
# ==========================================
with tab_png:
    st.subheader("Konversi PNG ke JPG")
    uploaded_pngs = st.file_uploader(
        "Pilih gambar PNG (bisa pilih banyak sekaligus)", 
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
                    # Tombol download HTML instan (bebas refresh)
                    html_jpg_button = f"""
                    <a href="data:image/jpeg;base64,{b64_jpg}" download="{jpg_filename}" style="text-decoration: none;">
                        <button style="
                            background-color: #FF4B4B;
                            color: white;
                            border: none;
                            padding: 8px 16px;
                            border-radius: 6px;
                            font-weight: 500;
                            font-size: 14px;
                            cursor: pointer;
                            display: inline-flex;
                            align-items: center;
                            gap: 5px;
                        ">
                            ⬇️ Unduh JPG
                        </button>
                    </a>
                    """
                    components.html(html_jpg_button, height=45)

            except Exception as e:
                st.error(f"Gagal mengonversi {file.name}: {e}")
