import React, { useEffect, useState } from "react";
import axios from "axios";

const ComplaintDetails = ({ complaintId }) => {
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComplaintDetails = async () => {
      const token = localStorage.getItem("access");

      try {
        const response = await axios.get(
          `http://127.0.0.1:8000/api/complaints/${complaintId}/`,
          {
            headers: {
              Authorization: `Token ${token}`,
            },
          }
        );
        setComplaint(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching complaint details:", error);
      }
    };

    fetchComplaintDetails();
  }, [complaintId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="complaint-details">
      <h1>{complaint.title}</h1>
      <p><strong>Descripción:</strong> {complaint.description}</p>
      <p><strong>Estado:</strong> {complaint.status}</p>
      <p><strong>Agente Asignado:</strong> {complaint.assigned_to.username}</p>
      <div>
        <h2>Historial</h2>
        <ul>
          {complaint.history.map((entry, index) => (
            <li key={index}>
              {entry.timestamp} - {entry.message}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ComplaintDetails;
