import io
import streamlit as st
from PIL import Image
import cairosvg

st.set_page_config(
    page_title="File Converter",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ File Converter")
st.caption("Konversi langsung tanpa ZIP — siap upload ke Microstock")

tab_svg, tab_png = st.tabs(["📐 SVG ke EPS", "🖼️ PNG ke JPG"])

# TAB SVG KE EPS
with tab_svg:
    st.subheader("Konversi SVG ke EPS")
    uploaded_svgs = st.file_uploader(
        "Pilih file SVG (bisa pilih banyak sekaligus)",
        accept_multiple_files=True
    )

    if uploaded_svgs:
        st.write(f"📁 Terdeteksi: **{len(uploaded_svgs)} file**")
        st.markdown("---")
        
        for idx, file in enumerate(uploaded_svgs):
            # Pastikan hanya memproses file berakhiran .svg
            if not file.name.lower().endswith(".svg"):
                continue

            base_name = file.name.rsplit(".", 1)[0]
            eps_name = f"{base_name}.eps"

            try:
                # Konversi langsung di memori
                svg_data = file.getvalue()
                eps_data = cairosvg.svg2eps(bytestring=svg_data)

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"✅ **{eps_name}**")
                with col2:
                    st.download_button(
                        label="⬇️ Download EPS",
                        data=eps_data,
                        file_name=eps_name,
                        mime="application/postscript",
                        key=f"dl_eps_{file.name}_{idx}"
                    )
            except Exception as e:
                st.error(f"Gagal mengonversi {file.name}: {e}")

# TAB PNG KE JPG
with tab_png:
    st.subheader("Konversi PNG ke JPG")
    uploaded_pngs = st.file_uploader(
        "Pilih file PNG (bisa pilih banyak sekaligus)",
        accept_multiple_files=True
    )

    if uploaded_pngs:
        st.write(f"📁 Terdeteksi: **{len(uploaded_pngs)} file**")
        st.markdown("---")

        for idx, file in enumerate(uploaded_pngs):
            if not file.name.lower().endswith(".png"):
                continue

            base_name = file.name.rsplit(".", 1)[0]
            jpg_name = f"{base_name}.jpg"

            try:
                img = Image.open(file)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=100, subsampling=0)
                jpg_data = buffer.getvalue()

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"✅ **{jpg_name}**")
                with col2:
                    st.download_button(
                        label="⬇️ Download JPG",
                        data=jpg_data,
                        file_name=jpg_name,
                        mime="image/jpeg",
                        key=f"dl_jpg_{file.name}_{idx}"
                    )
            except Exception as e:
                st.error(f"Gagal memproses {file.name}: {e}") 
