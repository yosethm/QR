import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"   # Solución al error de OpenMP

import streamlit as st
import qrcode
from PIL import Image
import io
import easyocr
import numpy as np

st.set_page_config(page_title="QR Generator", page_icon="🔳", layout="centered")

# --- Estilos CSS de alto nivel ---
st.markdown("""
<style>
/* Fondo animado */
.stApp {
    background: radial-gradient(circle at 20% 20%, rgba(110,231,255,0.15), transparent 25%),
                radial-gradient(circle at 80% 80%, rgba(167,139,250,0.15), transparent 25%),
                linear-gradient(135deg, #0b0f19 0%, #1c1f2b 100%);
    animation: bgmove 20s infinite alternate;
}
@keyframes bgmove {
    from {background-position: 0 0, 100% 100%, 0 0;}
    to   {background-position: 100% 0, 0 100%, 100% 100%;}
}

/* Títulos */
h1 {
    color: #fff !important;
    text-align: center;
    font-size: 2.5rem;
    background: linear-gradient(90deg, #6ee7ff, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 20px rgba(110,231,255,0.3);
    margin-bottom: 2rem;
}

/* Botones principales */
.stButton>button {
    background: linear-gradient(135deg, #6ee7ff, #a78bfa);
    border: none;
    border-radius: 14px;
    color: #fff;
    padding: 12px 25px;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 0.5px;
    box-shadow: 0 6px 20px rgba(110,231,255,0.4);
    cursor: pointer;
    transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
    transform: translateY(-4px) scale(1.05) rotateX(8deg);
    box-shadow: 0 10px 25px rgba(167,139,250,0.6);
}

/* Descarga */
.stDownloadButton>button {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    color: #fff;
    padding: 10px 20px;
    transition: all 0.3s ease-in-out;
}
.stDownloadButton>button:hover {
    background: rgba(167,139,250,0.2);
    transform: scale(1.05);
    box-shadow: 0 4px 15px rgba(110,231,255,0.4);
}

/* Caja de QR */
.qr-box {
    backdrop-filter: blur(12px);
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 8px 40px rgba(0,0,0,0.4);
    animation: fadeIn 1s ease-in-out;
    margin-top: 1.5rem;
    text-align: center;
}

/* Fade-in */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(15px);}
    to {opacity: 1; transform: translateY(0);}
}
img, .stImage, .stDownloadButton {
    animation: fadeIn 0.8s ease-in-out;
}

/* Área de texto */
textarea {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    padding: 10px;
    font-size: 1rem !important;
}

/* Selector de modo (radio como tabs) */
div[data-baseweb="radio"] > div {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
}
div[data-baseweb="radio"] label {
    background: rgba(255,255,255,0.08);
    padding: 10px 25px;
    border-radius: 30px;
    cursor: pointer;
    transition: all 0.3s ease-in-out;
    border: 1px solid rgba(255,255,255,0.25);
    color: #fff !important;
    font-weight: 600;
    font-size: 0.95rem;
}
div[data-baseweb="radio"] label:hover {
    background: rgba(110,231,255,0.15);
    transform: scale(1.05);
}
div[data-baseweb="radio"] input:checked + div {
    background: linear-gradient(135deg, #6ee7ff, #a78bfa);
    color: #000 !important;
    border: none;
    box-shadow: 0 4px 20px rgba(110,231,255,0.6);
}
</style>
""", unsafe_allow_html=True)

st.title("🔳 Generador de Códigos QR")

modo = st.radio("Elige una opción:", ["Texto", "Imagen con texto"])

def qr_to_bytes(qr_img):
    """Convierte un QR (PilImage) a bytes PNG."""
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

            st.markdown('<div class="qr-box">', unsafe_allow_html=True)
            st.image(qr_img, caption="Código QR")
            st.download_button("⬇️ Descargar PNG", img_bytes, "qr.png", "image/png")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Por favor escribe un texto.")

# --- Generar QR desde imagen (OCR) ---
elif modo == "Imagen con texto":
    archivo = st.file_uploader("Sube una imagen (JPG o PNG)", type=["png", "jpg", "jpeg"])
    if archivo is not None:
        imagen = Image.open(archivo)
        st.image(imagen, caption="Imagen subida", use_container_width=True)

        if st.button("Extraer texto y generar QR"):
            reader = easyocr.Reader(['es', 'en'])
            result = reader.readtext(np.array(imagen), detail=0)
            texto_extraido = " ".join(result).strip()

            if texto_extraido:
                qr = qrcode.QRCode(box_size=10, border=4)
                qr.add_data(texto_extraido)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")

                img_bytes, qr_img = qr_to_bytes(qr_img)

                st.markdown(f"**Texto detectado:** {texto_extraido}")
                st.markdown('<div class="qr-box">', unsafe_allow_html=True)
                st.image(qr_img, caption="Código QR")
                st.download_button("⬇️ Descargar PNG", img_bytes, "qr_from_image.png", "image/png")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ No se detectó texto en la imagen.")
