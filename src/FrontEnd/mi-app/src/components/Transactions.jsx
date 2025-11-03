import React, { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

export default function Transactions({ customerId }) {
    const [loading, setLoading] = useState(false);
    const [txs, setTxs] = useState([]);
    const [error, setError] = useState(null);
    const [expanded, setExpanded] = useState({});
    const [articleCache, setArticleCache] = useState({});

    useEffect(() => {
        if (!customerId) {
            setTxs([]);
            setError(null);
            setLoading(false);
            return;
        }
        setLoading(true);
        setError(null);
        fetch(`${API_BASE}/customers/${encodeURIComponent(customerId)}/transactions`)
            .then((r) => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.json();
            })
            .then((data) => setTxs(data.transactions || []))
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    }, [customerId]);

    const toggle = (key, articleId) => {
        setExpanded((s) => ({ ...s, [key]: !s[key] }));
        if (articleId && !articleCache[articleId]) fetchArticle(articleId);
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

    if (!customerId) return <div>Introduce un customer ID para ver transacciones.</div>;
    if (loading) return <div>Cargando transacciones…</div>;
    if (error) return <div style={{ color: "red" }}>Error: {error}</div>;
    if (!txs.length) return <div>No se encontraron transacciones.</div>;

    return (
        <div>
            <h3>Transacciones</h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {txs.map((t, i) => {
                    const key = t.transaction_id ?? t.id ?? i;
                    const article = t.article_id ?? t.article ?? null;
                    const date = t.transaction_date ?? t.date ?? "";
                    const cache = article ? articleCache[article] || {} : null;

                    return (
                        <li key={String(key)} style={{ padding: 8 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                                <div>
                                    <div style={{ fontWeight: 700 }}>Artículo: <span style={{ fontWeight: 600 }}>{String(article ?? "N/A")}</span></div>
                                    <div style={{ fontSize: 12, color: "var(--muted, #666)" }}>
                                        Transacción: <code style={{ fontSize: 12 }}>{String(key)}</code>
                                        {date ? " — " + date : ""}
                                    </div>
                                </div>
                                <div>
                                    <button
                                        onClick={() => toggle(key, article)}
                                        style={{
                                            padding: "6px 10px",
                                            borderRadius: 6,
                                            border: "1px solid var(--input-border, #d0d7de)",
                                            background: "transparent",
                                            cursor: "pointer",
                                        }}
                                    >
                                        {expanded[key] ? "Ocultar" : "Ver detalles"}
                                    </button>
                                </div>
                            </div>

                            {expanded[key] && (
                                <div style={{ marginTop: 8 }}>
                                    {article && cache && cache.loading && <div>Cargando info del artículo…</div>}
                                    {article && cache && cache.error && <div style={{ color: "red" }}>Error: {cache.error}</div>}
                                    {article && cache && cache.data && (
                                        <div style={{ background: "var(--panel-bg, #fff)", padding: 8, borderRadius: 6 }}>
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

                                            <div style={{ marginTop: 8, fontSize: 13, color: "var(--muted, #666)" }}>
                                                <strong>Otros datos:</strong>
                                                <ul style={{ paddingLeft: 12, marginTop: 6 }}>
                                                    {Object.entries(cache.data).map(([k, v]) => {
                                                        if (["prod_name","product_code","product_type_no","product_type_name","product_group_name","article_id"].includes(k)) return null;
                                                        return (
                                                            <li key={k}>
                                                                <code style={{ fontWeight:600 }}>{k}:</code> {v === null || v === undefined ? "—" : String(v)}
                                                            </li>
                                                        );
                                                    })}
                                                </ul>
                                            </div>
                                        </div>
                                    )}

                                    <pre style={{ marginTop: 8, whiteSpace: "pre-wrap", background: "rgba(0,0,0,0.03)", padding: 8, borderRadius: 6 }}>
                                        {JSON.stringify(t, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </li>
                    );
                })}
            </ul>
        </div>
    );
}