import { useEffect, useState } from 'react'
import './App.css'
import ImageUploader from './components/ImageUploader'

type Article = {
  id: string
  image_url: string
  data: Record<string, string>
}

type VisualHit = {
  id: string;
  score: number;
  image_url: string; // Añadir la propiedad image_url
  data: Record<string, string>;  // Añadir la propiedad data
};

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

async function dataURLtoFile(dataURL: string, filename = 'query.jpg'): Promise<File> {
  const res = await fetch(dataURL)
  const blob = await res.blob()
  return new File([blob], filename, { type: blob.type || 'image/jpeg' })
}

function App() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [queryId, setQueryId] = useState<string>('') // Query por ID
  const [result, setResult] = useState<Article | null>(null)
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)
  const [visualTopK, setVisualTopK] = useState<VisualHit[]>([])
  const [visualLoading, setVisualLoading] = useState(false)
  const [visualError, setVisualError] = useState<string | null>(null)

  const handleImageSelected = (imageData: string | null) => {
    setSelectedImage(imageData)
    setVisualTopK([]) // limpia estados visuales anteriores
    setVisualError(null)
  }

  // Llamada a handleSearchById
  const handleSearchById = async (id: string) => {
    const cleanedId = id.replace(/\.(jpg|png)$/, "");  // Quitar la extensión

    setSearchLoading(true)
    setSearchError(null)
    setResult(null)
    try {
      const res = await fetch(`${API_URL}/articles/${encodeURIComponent(cleanedId)}`)
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

  // Búsqueda visual por embeddings
const handleVisualSearch = async () => {
  if (!selectedImage) return;
  setVisualLoading(true);
  setVisualError(null);
  setVisualTopK([]);

  try {
    const file = await dataURLtoFile(selectedImage, 'query.jpg');
    const form = new FormData();
    form.append('file', file);

    const res = await fetch(`${API_URL}/visual/search?k=5`, {
      method: 'POST',
      body: form,
    });
    console.log(`URL de búsqueda visual: ${API_URL}/visual/search?k=5`);  // Log para verificar la URL visual
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(txt || `Error ${res.status}`);
    }
    const data = await res.json();
    console.log('Respuesta de búsqueda visual:', data); // Ver qué contiene `data`  
    setVisualTopK(data?.topk ?? []);

  } catch (err: any) {
    setVisualError(err?.message || 'Error en búsqueda visual');
  } finally {
    setVisualLoading(false);
  }
};

  useEffect(() => {
    if (selectedImage) {
      void handleVisualSearch() // Ejecuta la búsqueda visual
    }
  }, [selectedImage])

  return (
    <>
      <div className="flex flex-col items-center justify-center p-6 gap-6">
        <h1 className="text-3xl font-bold text-gray-800">Sistema de Recomendación</h1>

        {/* --- Buscador por ID --- */}
        <form onSubmit={(e) => { e.preventDefault(); handleSearchById(queryId) }} className="flex gap-2">
          <input
            value={queryId}
            onChange={(e) => setQueryId(e.target.value)}
            placeholder="Introduce un ID"
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
            <h2 className="text-lg font-semibold mb-2 text-gray-700">Resultado para ID: {result.id}</h2>
            {result.image_url ? (
              <img
                src={result.image_url.startsWith('http') ? result.image_url : `${API_URL}${result.image_url}`}
                alt={`Imagen ${result.id}`}
                className="max-h-64 rounded-xl shadow-md object-contain mx-auto"
              />
            ) : (
              <div className="text-sm text-gray-500">Imagen no encontrada</div>
            )}
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

        <ImageUploader onImageSelected={handleImageSelected} />

        {/* Resultados de búsqueda visual */}
        {selectedImage && (
          <div className="flex flex-row mt-2 text-center">
            <div className="flex flex-col gap-4 w-80">
              <img
                src={selectedImage}
                alt="Imagen seleccionada"
                className="w-full h-auto rounded-xl shadow-md object-contain"
              />
              {visualLoading && <div className="text-gray-600 text-sm">Buscando similares…</div>}
              {visualError && <div className="text-red-600 text-sm">{visualError}</div>}

              {/* Resultados Top-5 */}
              {visualTopK.length > 0 && (
                <div className="mt-2 w-full">
                  <h3 className="text-lg font-semibold text-gray-800">Similares (Top-5)</h3>
                  <ul className="mt-2 space-y-4 text-sm">
                    {visualTopK.map((r, i) => {
                      const imageUrl = r.image_url.startsWith('http') ? r.image_url : `${API_URL}${r.image_url}`;
                      console.log(`Imagen URL para el artículo ${r.id}:`, imageUrl);
                      console.log(`Data del artículo ${r.id}:`, r.data); // Ver qué data viene
                      
                      return (
                        <li key={`${r.id}-${i}`} className="flex flex-col border rounded px-3 py-2 bg-white shadow">
                          {/* Imagen */}
                          {r.image_url ? (
                            <img
                              src={imageUrl}
                              alt={`Imagen ${r.id}`}
                              className="max-h-48 w-auto rounded-xl shadow-md object-contain mx-auto mb-3"
                            />
                          ) : (
                            <div className="text-sm text-gray-500 mb-3">Imagen no disponible</div>
                          )}
                          
                          {/* Información del artículo */}
                          <div className="text-left">
                            <h4 className="text-sm font-semibold mb-2">ID: {r.id}</h4>
                            <span className="text-xs text-gray-500 mb-2 block">Score: {r.score.toFixed(4)}</span>
                            
                            {/* Tabla con todos los datos del CSV */}
                            {r.data && Object.keys(r.data).length > 0 ? (
                              <table className="w-full text-xs border-collapse mt-2">
                                <tbody>
                                  {Object.entries(r.data).map(([key, value]) => (
                                    <tr key={key} className="border-b">
                                      <td className="py-1 pr-2 font-semibold text-gray-700 align-top">{key}</td>
                                      <td className="py-1 text-gray-600">{value}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            ) : (
                              <div className="text-xs text-gray-500">Sin datos adicionales</div>
                            )}
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
              <button
                className="bg-blue-500 text-white px-4 py-2 rounded-md disabled:opacity-60"
                onClick={handleVisualSearch}
                disabled={visualLoading}
              >
                {visualLoading ? 'Buscando…' : 'Reintentar búsqueda visual'}
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  )
}

export default App
