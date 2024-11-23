import React, { useEffect, useState } from "react";
import axios from "axios";

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const handleLogout = () => {
    localStorage.removeItem("access"); // Elimina el token de acceso
    localStorage.removeItem("refresh"); // Si tienes un token de refresco
    window.location.href = "/"; // Redirige al usuario al login
  };

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("access"); // Recupera el token desde localStorage
      if (!token) {
        alert("No tienes un token válido, por favor inicia sesión nuevamente.");
        window.location.href = "/";
        return;
      }

      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/api/complaints/dashboard/",
          {
            headers: {
              Authorization: `Token ${token}`, // Asegúrate que este formato sea correcto en tu backend
            },
          }
        );
        setData(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        if (error.response && error.response.status === 401) {
          alert("Token inválido o expirado. Por favor, inicia sesión de nuevo.");
          handleLogout(); // Elimina el token y redirige al login
        }
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Dashboard Analítico</h1>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </header>
      <div>
        <h2>Total de Quejas</h2>
        <p>{data.total_complaints}</p>
      </div>
      <div>
        <h2>Quejas por Estado</h2>
        <ul>
          {data.complaints_by_status.map((status) => (
            <li key={status.status}>
              {status.status}: {status.count}
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h2>Tiempo Promedio de Resolución</h2>
        <p>{(data.avg_resolution_time / 60).toFixed(2)} minutos</p>
      </div>
      <div>
        <h2>Carga por Agente</h2>
        <ul>
          {data.agents_load.map((agent) => (
            <li key={agent.assigned_to__username}>
              {agent.assigned_to__username}: {agent.count}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
