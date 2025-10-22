import { useState } from 'react'
import './App.css'
import ImageUploader from './components/ImageUploader'
import { getProductData, getProductImage } from './api/api' // <- tu API client

// ---- Tipos para la búsqueda por ID (endpoint /articles/:id)
type Article = {
  id: string
  image_url: string
  data: Record<string, string>
}

// Base de API (para pintar la imagen devuelta por /articles/:id)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

function App() {
  // ---- Estados comunes
  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  // ---- Estados búsqueda por ID (GET /articles/:id)
  const [queryId, setQueryId] = useState<string>('')
  const [result, setResult] = useState<Article | null>(null)
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)

  // ---- Estados flujo "Continuar" (usar api.ts -> getProductData/getProductImage)
  const [productLoading, setProductLoading] = useState(false)
  const [productError, setProductError] = useState<string | null>(null)
  const [productData, setProductData] = useState<any>(null)
  const [productImageUrl, setProductImageUrl] = useState<string | null>(null)

  // ---- Handlers
  const handleImageSelected = (imageData: string | null) => {
    setSelectedImage(imageData)
    // al elegir imagen, limpiamos resultados previos del flujo de producto
    setProductData(null)
    setProductImageUrl(null)
    setProductError(null)
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    const id = queryId.trim()
    if (!id) return
    setSearchLoading(true)
    setSearchError(null)
    setResult(null)
    try {
      const res = await fetch(`${API_URL}/articles/${encodeURIComponent(id)}`)
      if (!res.ok) {
        const msg = await res.text()
        throw new Error(msg || `Error ${res.status}`)
      }
      const data: Article = await res.json()
      setResult(data)
    } catch (err: any) {
      setSearchError(err.message || 'Error al buscar el ID')
    } finally {
      setSearchLoading(false)
    }
  }

  // Usa tu client de api.ts (puedes cambiar el ID fijo por el queryId si te interesa)
  const handleGetProduct = async () => {
    setProductLoading(true)
    setProductError(null)
    setProductData(null)
    setProductImageUrl(null)
    try {
      // Si quieres usar el ID del input, intenta parsearlo, si no, usa 1
      const idFromInput = Number.parseInt(queryId, 10)
      const id = Number.isFinite(idFromInput) ? idFromInput : 1

      const data = await getProductData(id)
      setProductData(data)
      console.log('Producto:', data)

      const imageResp = await getProductImage(id)
      // asume que la API devuelve { image_url: "/path" } o una URL absoluta
      const imgUrl: string =
        imageResp?.image_url?.startsWith('http')
          ? imageResp.image_url
          : `${API_URL}${imageResp?.image_url || ''}`

      setProductImageUrl(imgUrl)
      console.log('Imagen:', imageResp)
    } catch (error: any) {
      console.error('Error llamando al backend:', error)
      setProductError(error?.response?.data?.detail || error?.message || 'Error al obtener producto')
    } finally {
      setProductLoading(false)
    }
  }

  return (
    <>
      <div className="flex flex-col items-center justify-center p-6 gap-6">
        <h1 className="text-3xl font-bold text-gray-800">
          Sistema de Recomendación
        </h1>

        {/* --- Buscador por ID (endpoint /articles/:id) --- */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            value={queryId}
            onChange={(e) => setQueryId(e.target.value)}
            placeholder="Introduce un ID (ej. 12345)"
            className="border rounded px-3 py-2"
          />
          <button
            type="submit"
            disabled={searchLoading}
            className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-60"
          >
            {searchLoading ? 'Buscando...' : 'Buscar'}
          </button>
        </form>

        {searchError && <div className="text-red-600">{searchError}</div>}

        {result && (
          <div className="mt-2 text-center">
            <h2 className="text-lg font-semibold mb-2 text-gray-700">
              Resultado para ID: {result.id}
            </h2>
            {result.image_url ? (
              <img
                src={result.image_url.startsWith('http') ? result.image_url : `${API_URL}${result.image_url}`}
                alt={`Imagen ${result.id}`}
                className="max-h-64 rounded-xl shadow-md object-contain mx-auto"
              />
            ) : (
              <div className="text-sm text-gray-500">Imagen no encontrada</div>
            )}
            {/* Tabla de atributos */}
            {Object.keys(result.data || {}).length > 0 && (
              <table className="min-w-[320px] mt-4 border-collapse">
                <tbody>
                  {Object.entries(result.data).map(([k, v]) => (
                    <tr key={k}>
                      <td className="border px-2 py-1 font-semibold align-top">{k}</td>
                      <td className="border px-2 py-1">{v}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* --- Subida de imagen + confirmación --- */}
        <ImageUploader onImageSelected={handleImageSelected} />

        {selectedImage && (
          <div className="flex flex-row mt-2 text-center">
            <div className="flex flex-col gap-4 w-72">
              <img
                src={selectedImage}
                alt="Imagen seleccionada"
                className="w-full h-auto rounded-xl shadow-md object-contain"
              />
              <h2 className="text-base font-semibold text-gray-700">
                ¿Estás seguro de que quieres obtener recomendaciones para este producto?
              </h2>

              {/* Botones */}
              <div className="flex flex-row justify-evenly">
                <button
                  className="bg-blue-500 text-white px-4 py-2 rounded-md disabled:opacity-60"
                  onClick={handleGetProduct}
                  disabled={productLoading}
                >
                  {productLoading ? 'Cargando…' : 'Continuar'}
                </button>
                <button
                  className="bg-red-500 text-white px-4 py-2 rounded-md"
                  onClick={() => setSelectedImage(null)}
                >
                  Cancelar
                </button>
              </div>

              {/* Estado del flujo de producto */}
              {productError && (
                <div className="text-red-600 text-sm">{productError}</div>
              )}

              {(productData || productImageUrl) && (
                <div className="flex flex-col gap-2">
                  {productImageUrl && (
                    <img
                      src={productImageUrl}
                      alt="Imagen del producto"
                      className="w-full h-auto rounded-lg shadow"
                    />
                  )}
                  {productData && (
                    <pre className="text-left text-xs bg-gray-100 p-2 rounded overflow-x-auto max-h-60">
{JSON.stringify(productData, null, 2)}
                    </pre>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  )
}

export default App
