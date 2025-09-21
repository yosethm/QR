import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"   # Solución al error de OpenMP

import streamlit as st
import qrcode
from PIL import Image
import io
import easyocr
import numpy as np

st.set_page_config(page_title="QR Generator", page_icon="🔳", layout="centered")

# --- Estilos CSS ---
st.markdown("""
<style>
body, .stApp { background-color: #0b0f19; color: #f1f1f1; }
h1, h2, h3, label, p, span, div { color: #f1f1f1 !important; }
.stButton>button {
  background: #6ee7ff22; border: 1px solid #6ee7ff55; border-radius: 12px; color: #fff; padding: 8px 18px;
}
.stButton>button:hover { background: #6ee7ff44; }
.qr-box { background: rgba(255,255,255,0.06); padding: 20px; border-radius: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🔳 Generador de Códigos QR")

modo = st.radio("Elige una opción:", ["Texto", "Imagen con texto"])

def qr_to_bytes(qr_img):
    """Convierte un QR (PilImage) a bytes PNG."""
    # Convertir explícitamente a PIL.Image.Image
    if not isinstance(qr_img, Image.Image):
        qr_img = qr_img.get_image()
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    return buf.getvalue(), qr_img

# --- Generar QR desde texto ---
if modo == "Texto":
    texto = st.text_area("Escribe el texto para el QR:")
    if st.button("Generar QR"):
        if texto.strip():
            qr = qrcode.QRCode(box_size=10, border=4)
            qr.add_data(texto.strip())
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            img_bytes, qr_img = qr_to_bytes(qr_img)

            st.image(qr_img, caption="Código QR")
            st.download_button("⬇️ Descargar PNG", img_bytes, "qr.png", "image/png")
        else:
            st.warning("⚠️ Por favor escribe un texto.")

# --- Generar QR desde imagen (OCR) ---
elif modo == "Imagen con texto":
    archivo = st.file_uploader("Sube una imagen (JPG o PNG)", type=["png", "jpg", "jpeg"])
    if archivo is not None:
        imagen = Image.open(archivo)
        st.image(imagen, caption="Imagen subida", use_container_width=True)

        if st.button("Extraer texto y generar QR"):
            reader = easyocr.Reader(['es', 'en'])  # soporta español e inglés
            result = reader.readtext(np.array(imagen), detail=0)
            texto_extraido = " ".join(result).strip()

            if texto_extraido:
                qr = qrcode.QRCode(box_size=10, border=4)
                qr.add_data(texto_extraido)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")

                img_bytes, qr_img = qr_to_bytes(qr_img)

                st.markdown(f"**Texto detectado:** {texto_extraido}")
                st.image(qr_img, caption="Código QR")
                st.download_button("⬇️ Descargar PNG", img_bytes, "qr_from_image.png", "image/png")
            else:
                st.warning("⚠️ No se detectó texto en la imagen.")
