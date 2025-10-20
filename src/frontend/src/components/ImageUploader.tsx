import { useState } from "react"

interface ImageUploaderProps {
  onImageSelected: (imageData: string | null) => void
}


export default function ImageUploader({ onImageSelected }: ImageUploaderProps) {
  const [image, setImage] = useState<string | null>(null)

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) {
        e.target.value = "" 
        return
    }
    const reader = new FileReader()
    reader.onloadend = () => {
      const result = reader.result as string
      setImage(result)
      onImageSelected(null)
    }
    reader.readAsDataURL(file)
    e.target.value = ""
  }

  const handleAccept = () => {
    onImageSelected(image)
    setImage(null)
  }

  const handleCancel = () => {
    setImage(null)
    onImageSelected(null)
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 w-full max-w-md flex flex-col items-center">
      <label
        htmlFor="imageUpload"
        className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg mb-4 transition"
      >
        Subir imagen
      </label>
      <input
        id="imageUpload"
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
        className="hidden"
      />
      {image ? (
        <div className="flex flex-col gap-4"> 
          <img
            src={image}
            alt="Vista previa"
            className="mt-4 rounded-xl shadow-md max-h-96 object-contain"
          />
          <div className="flex justify-center gap-4">
            <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg mr-2 transition"
                onClick={handleAccept}
            >
              Aceptar
            </button>
            <button 
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition"
                onClick={handleCancel}
            >
              Borrar
            </button>
          </div>
        </div>
      ) : (
        <p className="text-gray-500">No se ha seleccionado ninguna imagen.</p>
      )}
    </div>
  )
}