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
    uploaded_svgs = st.file_uploader(
        "Pilih file SVG", 
        type=["svg"], 
        accept_multiple_files=True,
        key="svg_uploader"
    )
    
    if uploaded_svgs:
        for file in uploaded_svgs:
            st.divider()
            st.write(f"📁 **{file.name}**")
            try:
                svg_data = file.read()
                eps_output = cairosvg.svg2ps(bytestring=svg_data)
                output_name = file.name.rsplit(".", 1)[0] + ".eps"
                
                st.download_button(
                    label=f"⬇️ Download {output_name}",
                    data=eps_output,
                    file_name=output_name,
                    mime="application/postscript",
                    key=f"dl_eps_{file.name}"
                )
            except Exception as e:
                st.error(f"Gagal mengonversi {file.name}: {e}")

# TAB PNG KE JPG
with tab_png:
    st.subheader("Konversi PNG ke JPG")
    uploaded_pngs = st.file_uploader(
        "Pilih file PNG", 
        type=["png"], 
        accept_multiple_files=True,
        key="png_uploader"
    )
    
    if uploaded_pngs:
        for file in uploaded_pngs:
            st.divider()
            st.write(f"📁 **{file.name}**")
            try:
                img = Image.open(file)
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    canvas = Image.new("RGB", img.size, (255, 255, 255))
                    alpha_img = img.convert("RGBA")
                    canvas.paste(alpha_img, mask=alpha_img.split()[3])
                    final_img = canvas
                else:
                    final_img = img.convert("RGB")
                
                jpg_buffer = io.BytesIO()
                final_img.save(jpg_buffer, format="JPEG", quality=98, subsampling=0)
                jpg_buffer.seek(0)
                
                output_name = file.name.rsplit(".", 1)[0] + ".jpg"
                
                st.download_button(
                    label=f"⬇️ Download {output_name}",
                    data=jpg_buffer.getvalue(),
                    file_name=output_name,
                    mime="image/jpeg",
                    key=f"dl_jpg_{file.name}"
                )
            except Exception as e:
                st.error(f"Gagal mengonversi {file.name}: {e}")
