import React, { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

export default function Recommendations({ customerId, topK = 5 }) {
    const [loading, setLoading] = useState(false);
    const [recs, setRecs] = useState([]);
    const [error, setError] = useState(null);
    const [expanded, setExpanded] = useState({}); // map article_id -> bool
    const [articleCache, setArticleCache] = useState({}); // article_id -> data or {loading:true, error}

    useEffect(() => {
        if (!customerId) {
            setRecs([]);
            setError(null);
            setLoading(false);
            return;
        }
        setLoading(true);
        setError(null);
        fetch(`${API_BASE}/recommendations/${encodeURIComponent(customerId)}?top_k=${encodeURIComponent(topK)}`)
            .then((r) => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.json();
            })
            .then((data) => setRecs(data.recommendations || []))
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    }, [customerId, topK]);

    const toggle = (id) => {
        setExpanded((s) => ({ ...s, [id]: !s[id] }));
        if (!articleCache[id]) fetchArticle(id);
    };

    const fetchArticle = async (articleId) => {
        if (!articleId) return;
        setArticleCache((c) => ({ ...c, [articleId]: { loading: true } }));
        try {
            const res = await fetch(`${API_BASE}/articles/${encodeURIComponent(String(articleId))}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setArticleCache((c) => ({ ...c, [articleId]: { data } }));
        } catch (err) {
            setArticleCache((c) => ({ ...c, [articleId]: { error: err.message } }));
        }
    };

    if (!customerId) return <div>Introduce un customer ID para ver recomendaciones.</div>;
    if (loading) return <div>Cargando recomendaciones…</div>;
    if (error) return <div style={{ color: "red" }}>Error cargando recomendaciones: {error}</div>;
    if (!recs.length) return <div>No se encontraron recomendaciones.</div>;

    return (
        <div>
            <h3>Recomendaciones</h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {recs.map((r) => {
                    const id = r.article_id ?? r.id ?? Math.random();
                    const name = r.prod_name ?? r.name ?? "Artículo sin nombre";
                    const score = typeof r.score === "number" ? r.score.toFixed(3) : String(r.score);
                    const cache = articleCache[id] || {};
                    return (
                        <li key={String(id)} style={{ padding: 8 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                                <div>
                                    <div style={{ fontWeight: 700 }}>{name}</div>
                                    <div style={{ fontSize: 12, color: "var(--muted, #666)" }}>
                                        ID: <code style={{ fontSize: 12 }}>{String(id)}</code>
                                    </div>
                                </div>
                                <div style={{ textAlign: "right" }}>
                                    <div style={{ fontWeight: 700 }}>{score}</div>
                                    <button
                                        onClick={() => toggle(id)}
                                        style={{
                                            marginTop: 6,
                                            padding: "6px 10px",
                                            borderRadius: 6,
                                            border: "1px solid var(--input-border, #d0d7de)",
                                            background: "transparent",
                                            cursor: "pointer",
                                        }}
                                    >
                                        {expanded[id] ? "Ocultar" : "Detalles"}
                                    </button>
                                </div>
                            </div>

                            {expanded[id] && (
                                <div style={{ marginTop: 8 }}>
                                    {cache.loading && <div>Cargando info del artículo…</div>}
                                    {cache.error && <div style={{ color: "red" }}>Error: {cache.error}</div>}
                                    {cache.data && (
                                        <div style={{ background: "var(--panel-bg, #fff)", padding: 8, borderRadius: 6 }}>
                                            {/* Mostrar campos que existen en tu tabla articles */}
                                            <div><strong>Nombre:</strong> {cache.data.prod_name ?? "—"}</div>
                                            <div style={{ marginTop: 6 }}>
                                                <strong>Código:</strong> {cache.data.product_code ?? "—"}
                                            </div>
                                            <div style={{ marginTop: 6 }}>
                                                <strong>Tipo (id):</strong> {cache.data.product_type_no ?? "—"}
                                            </div>
                                            <div style={{ marginTop: 6 }}>
                                                <strong>Tipo:</strong> {cache.data.product_type_name ?? "—"}
                                            </div>
                                            <div style={{ marginTop: 6 }}>
                                                <strong>Grupo:</strong> {cache.data.product_group_name ?? "—"}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </li>
                    );
                })}
            </ul>
        </div>
    );
}