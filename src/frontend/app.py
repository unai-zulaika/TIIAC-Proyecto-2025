import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# URL base de tu backend FastAPI (ajusta según tu servidor)
BASE_URL = "http://localhost:8000"

st.title("Visualizador de Productos")

# Input para el ID del producto
product_id = st.number_input("Introduce el ID del producto", min_value=1, step=1)

if st.button("Buscar producto"):
    # Llamada para obtener datos del producto
    data_url = f"{BASE_URL}/get_product_data?id={product_id}"
    try:
        response_data = requests.get(data_url, timeout=10)
    except Exception as e:
        st.error(f"Error conectando con el backend: {e}")
    else:
        if response_data.status_code == 200:
            product_data = response_data.json()
            st.write("### Datos del producto:")
            st.json(product_data)

            # Llamada para obtener imagen (devuelve URL presignada)
            image_url_endpoint = f"{BASE_URL}/get_product_image?id={product_id}"
            try:
                response_image = requests.get(image_url_endpoint, timeout=10)
            except Exception as e:
                st.warning(f"No se pudo solicitar la imagen: {e}")
            else:
                if response_image.status_code == 200:
                    image_data = response_image.json()
                    st.image(image_data.get("image_url"), caption=f"Producto {product_id}")
                elif response_image.status_code == 404:
                    st.warning("Imagen no encontrada para este producto.")
                else:
                    st.warning(f"Error al obtener imagen: {response_image.status_code}")
        elif response_data.status_code == 404:
            st.error("Producto no encontrado.")
        else:
            st.error(f"Error al obtener datos: {response_data.status_code}")

