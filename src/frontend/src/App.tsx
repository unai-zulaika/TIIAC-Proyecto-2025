import { useState } from 'react'
import './App.css'
import ImageUploader from './components/ImageUploader'
import { getProductData, getProductImage } from './api/api.ts'

function App() {

  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  // const [productData, setProductData] = useState<any>(null)

  const handleImageSelected = (imageData: string | null) => {
    setSelectedImage(imageData)
  }

  const handleGetProduct = async () => {
    try {
      const product = await getProductData(1); // id=1
      console.log('Producto:', product);

      const image = await getProductImage(1);
      console.log('Imagen:', image);
    } catch (error) {
      console.error('Error llamando al backend:', error);
    }

    // try {
    //   const productId = 1; // Ejemplo: ID fijo, o puedes obtenerlo de un input
    //   const data = await getProductData(productId);
    //   setProductData(data);
    //   console.log(productData);

    //   const imageResponse = await getProductImage(productId);
    //   setSelectedImage(imageResponse.image_url);
    // } catch (error: any) {
    //   alert(error.response?.data?.detail || 'Error al obtener producto');
    // }
  }

  return (
    <>
      {/* <div className="text-center text-4xl font-bold text-blue-600 mt-10">
        holaaaa caracola
      </div> */}

      <div className="flex flex-col items-center justify-center p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Sistema de Recomendación
        </h1>
        <ImageUploader onImageSelected={handleImageSelected}/>

        {selectedImage && (
          <div className="flex flex-row mt-6 text-center">
            <div className='flex flex-col gap-4 w-72'>
              <img
                src={selectedImage}
                alt="Imagen seleccionada"
                className="w-full h-auto rounded-xl shadow-md object-contain"
              />
              <h1 className="text-base font-semibold text-gray-700">
                ¿Estas seguro que quieres obtener recomendaciones para este producto?
              </h1>
                
              <div className='flex flex-row justify-evenly'>
                <button
                  className='bg-blue-500 text-white px-4 py-2 rounded-md'
                  onClick={handleGetProduct}
                >
                  Continuar
                </button>
                <button 
                  className='bg-red-500 text-white px-4 py-2 rounded-md'
                  onClick={() => setSelectedImage(null)}
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}

export default App
