import React, { useEffect, useState } from "react";
import axios from "axios";

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/complaints/dashboard/", {
          headers: {
            Authorization: `Token ${localStorage.getItem("authToken")}`,
          },
        });
        setData(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <h1>Dashboard Analítico</h1>
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
