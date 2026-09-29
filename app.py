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
st.caption("Konversi SVG ➔ EPS (Vektor Utuh) & PNG ➔ JPG (Kualitas Maksimal)")

tab_svg, tab_png = st.tabs(["📐 SVG ke EPS", "🖼️ PNG ke JPG"])

# ==========================================
# TAB SVG KE EPS (TETAP SAMA SEPERTI ASLINYA)
# ==========================================
with tab_svg:
    st.subheader("Konversi SVG ke EPS")
    uploaded_svg = st.file_uploader("Pilih file SVG", type=["svg"])

    if uploaded_svg is not None:
        svg_bytes = uploaded_svg.getvalue()
        base_name = uploaded_svg.name.rsplit(".", 1)[0]
        eps_filename = f"{base_name}.eps"

        try:
            eps_data = cairosvg.svg2eps(bytestring=svg_bytes)
            st.success("✅ File siap diunduh!")
            st.download_button(
                label="⬇️ Download File EPS",
                data=eps_data,
                file_name=eps_filename,
                mime="application/postscript"
            )
        except Exception as e:
            st.error(f"Gagal mengonversi file: {e}")

# ==========================================
# TAB PNG KE JPG (BISA MULTI-FILE & TANPA REFRESH)
# ==========================================
with tab_png:
    st.subheader("Konversi PNG ke JPG (Bisa Banyak File)")
    uploaded_pngs = st.file_uploader(
        "Pilih gambar PNG (bisa pilih banyak sekaligus)", 
        type=["png"], 
        accept_multiple_files=True
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
                b64_str = base64.b64encode(jpg_bytes).decode()

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"🖼️ **{jpg_filename}**")
                with col2:
                    # Tombol download instan langsung lewat browser (TIDAK ME-REFRESH HALAMAN)
                    html_download_button = f"""
                    <a href="data:image/jpeg;base64,{b64_str}" download="{jpg_filename}" style="text-decoration: none;">
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
                    components.html(html_download_button, height=45)

            except Exception as e:
                st.error(f"Gagal mengonversi {file.name}: {e}") 
