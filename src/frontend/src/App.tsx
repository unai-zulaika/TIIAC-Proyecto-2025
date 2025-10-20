import { useState } from 'react'
import './App.css'
import ImageUploader from './components/ImageUploader'

function App() {

  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  const handleImageSelected = (imageData: string | null) => {
    setSelectedImage(imageData)
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
          <div className="mt-6 text-center">
            <h2 className="text-lg font-semibold mb-2 text-gray-700">
              Imagen seleccionada en el componente padre:
            </h2>
            <img
              src={selectedImage}
              alt="Imagen seleccionada"
              className="max-h-64 rounded-xl shadow-md object-contain"
            />
          </div>
        )}
      </div>
    </>
  )
}

export default App
