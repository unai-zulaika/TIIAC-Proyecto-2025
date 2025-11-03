import React, { useState } from "react";
import Recommendations from "../components/Recommendations";
import Transactions from "../components/Transactions";

export default function Home() {
    const [customerId, setCustomerId] = useState("");
    const [view, setView] = useState("transactions"); // "transactions" | "recommendations"

    return (
        <div className="centered-container">
            <div className="panel">
                <h1 className="panel-title">Panel de Usuario</h1>

                <div className="input-row">
                    <label>Customer ID:</label>
                    <input
                        value={customerId}
                        onChange={(e) => setCustomerId(e.target.value)}
                        placeholder="Introduce customer id..."
                        className="customer-input"
                    />
                </div>

                <div className="view-toggle">
                    <button
                        className={`toggle-btn ${view === "transactions" ? "active" : ""}`}
                        onClick={() => setView("transactions")}
                        aria-pressed={view === "transactions"}
                    >
                        Transacciones
                    </button>
                    <button
                        className={`toggle-btn ${view === "recommendations" ? "active" : ""}`}
                        onClick={() => setView("recommendations")}
                        aria-pressed={view === "recommendations"}
                    >
                        Recomendaciones
                    </button>
                </div>

                <div className="content-area">
                    {view === "transactions" && <Transactions customerId={customerId} />}
                    {view === "recommendations" && <Recommendations customerId={customerId} />}
                </div>
            </div>
        </div>
    );
}
