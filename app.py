import io
import streamlit as st
from PIL import Image
import cairosvg

st.set_page_config(
    page_title="Batch Converter (No ZIP)",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Batch File Converter")
st.caption("Konversi banyak file sekaligus tanpa ZIP — langsung download per file!")

tab_svg, tab_png = st.tabs(["📐 SVG ke EPS", "🖼️ PNG ke JPG"])

# TAB SVG KE EPS
with tab_svg:
    st.subheader("Konversi SVG ke EPS")
    uploaded_svgs = st.file_uploader(
        "Pilih beberapa file SVG sekaligus",
        type=["svg"],
        accept_multiple_files=True,
        key="uploader_svg_list"
    )

    if uploaded_svgs:
        st.write(f"Total file: **{len(uploaded_svgs)} file**")
        
        if st.button("🚀 Konversi Semua SVG", key="convert_all_svg"):
            results = []
            with st.spinner("Sedang mengonversi semua file SVG ke EPS..."):
                for uploaded_file in uploaded_svgs:
                    try:
                        svg_bytes = uploaded_file.getvalue()
                        eps_data = cairosvg.svg2eps(bytestring=svg_bytes)
                        base_name = uploaded_file.name.rsplit(".", 1)[0]
                        results.append({
                            "name": f"{base_name}.eps",
                            "data": eps_data
                        })
                    except Exception as e:
                        st.error(f"Gagal mengonversi {uploaded_file.name}: {e}")
            st.session_state["converted_eps"] = results

        # Tampilkan daftar file hasil konversi
        if "converted_eps" in st.session_state and st.session_state["converted_eps"]:
            st.success("✅ Semua file selesai dikonversi! Tinggal tap download:")
            for idx, item in enumerate(st.session_state["converted_eps"]):
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"📄 **{item['name']}**")
                with col2:
                    st.download_button(
                        label="⬇️ Download EPS",
                        data=item["data"],
                        file_name=item["name"],
                        mime="application/postscript",
                        key=f"dl_eps_{idx}"
                    )

# TAB PNG KE JPG
with tab_png:
    st.subheader("Konversi PNG ke JPG")
    uploaded_pngs = st.file_uploader(
        "Pilih beberapa file PNG sekaligus",
        type=["png"],
        accept_multiple_files=True,
        key="uploader_png_list"
    )

    if uploaded_pngs:
        st.write(f"Total gambar: **{len(uploaded_pngs)} file**")
        
        if st.button("🚀 Konversi Semua PNG", key="convert_all_png"):
            results_png = []
            with st.spinner("Sedang memproses seluruh gambar JPG..."):
                for uploaded_file in uploaded_pngs:
                    try:
                        image = Image.open(uploaded_file)
                        if image.mode in ("RGBA", "P"):
                            image = image.convert("RGB")
                        
                        jpg_buffer = io.BytesIO()
                        image.save(jpg_buffer, format="JPEG", quality=100, subsampling=0)
                        
                        base_name = uploaded_file.name.rsplit(".", 1)[0]
                        results_png.append({
                            "name": f"{base_name}.jpg",
                            "data": jpg_buffer.getvalue()
                        })
                    except Exception as e:
                        st.error(f"Gagal mengonversi {uploaded_file.name}: {e}")
            st.session_state["converted_jpg"] = results_png

        # Tampilkan daftar file hasil konversi
        if "converted_jpg" in st.session_state and st.session_state["converted_jpg"]:
            st.success("✅ Semua file selesai dikonversi! Tinggal tap download:")
            for idx, item in enumerate(st.session_state["converted_jpg"]):
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"🖼️ **{item['name']}**")
                with col2:
                    st.download_button(
                        label="⬇️ Download JPG",
                        data=item["data"],
                        file_name=item["name"],
                        mime="image/jpeg",
                        key=f"dl_jpg_{idx}"
                    )
