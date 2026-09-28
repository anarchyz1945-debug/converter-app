import io
import streamlit as st
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

# TAB SVG KE EPS
with tab_svg:
    st.subheader("Konversi SVG ke EPS")
    uploaded_svg = st.file_uploader("Pilih file SVG", type=["svg"], key="svg_uploader")

    if uploaded_svg is not None:
        svg_bytes = uploaded_svg.getvalue()
        
        # Buat nama file download
        base_name = uploaded_svg.name.rsplit(".", 1)[0]
        eps_filename = f"{base_name}.eps"

        with st.spinner("Memproses konversi vektor..."):
            try:
                # Konversi langsung sekali saja ke memori
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

# TAB PNG KE JPG
with tab_png:
    st.subheader("Konversi PNG ke JPG")
    uploaded_png = st.file_uploader("Pilih file PNG", type=["png"], key="png_uploader")

    if uploaded_png is not None:
        base_name_png = uploaded_png.name.rsplit(".", 1)[0]
        jpg_filename = f"{base_name_png}.jpg"

        with st.spinner("Memproses gambar JPG kualitas maksimal..."):
            try:
                image = Image.open(uploaded_png)
                
                # Ubah format jika ada transparansi RGBA ke RGB dengan background putih
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                
                jpg_buffer = io.BytesIO()
                image.save(jpg_buffer, format="JPEG", quality=100, subsampling=0)
                jpg_data = jpg_buffer.getvalue()

                st.success("✅ File siap diunduh!")
                st.download_button(
                    label="⬇️ Download File JPG",
                    data=jpg_data,
                    file_name=jpg_filename,
                    mime="image/jpeg"
                )
            except Exception as e:
                st.error(f"Gagal mengonversi gambar: {e}")
