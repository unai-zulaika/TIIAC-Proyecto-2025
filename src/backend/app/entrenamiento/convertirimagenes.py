import torch
import os
import numpy as np
from PIL import Image
from torchvision import transforms
from autoencoder import Encoder  # Importar solo el encoder

# Paso 1: Cargar el modelo del encoder
model = Encoder(emb_dim=256)  # Asegúrate de que emb_dim coincida con el usado en tu entrenamiento
model.load_state_dict(torch.load('encoder.pth', map_location=torch.device('cpu')))
model.eval()  # Poner el modelo en modo de evaluación

# Paso 2: Definir las transformaciones necesarias para las imágenes
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalización de imagen
])

# Paso 3: Carpeta con las imágenes
image_folder = 'C:/Users/joorg/Documents/UNI/5/ia/TIIAC-Proyecto-2025/data/img'  # Cambia esto por la ruta correcta de las imágenes
output_file = 'image_embeddings.npz'  # Archivo de salida para los embeddings

# Paso 4: Crear listas para almacenar embeddings y sus identificadores
embeddings = []
image_ids = []

# Paso 5: Recorrer todas las imágenes y procesarlas
for img_name in os.listdir(image_folder):
    img_path = os.path.join(image_folder, img_name)
    
    # Asegúrate de que es un archivo de imagen
    if img_path.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        image = Image.open(img_path)
        image = transform(image).unsqueeze(0)  # Añadir la dimensión del batch
        
        # Paso 6: Obtener el embedding de la imagen
        with torch.no_grad():
            embedding = model(image)
        
        # Guardar el embedding y el nombre de la imagen
        embeddings.append(embedding.cpu().numpy())
        image_ids.append(img_name)

# Paso 7: Guardar los embeddings y los identificadores en un archivo .npz
np.savez(output_file, embeddings=np.vstack(embeddings), ids=image_ids)

print(f"Embeddings guardados en {output_file}")
