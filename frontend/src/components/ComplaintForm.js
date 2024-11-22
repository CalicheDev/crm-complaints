import React, { useState } from "react";

const ComplaintForm = () => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/api/complaints/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`, // Incluye el token si usas autenticación
        },
        body: JSON.stringify({ title, description }),
      });

      if (response.ok) {
        setMessage("¡Queja enviada con éxito!");
        setTitle("");
        setDescription("");
      } else {
        setMessage("Hubo un error al enviar la queja. Inténtalo de nuevo.");
      }
    } catch (error) {
      console.error("Error:", error);
      setMessage("Error al conectar con el servidor.");
    }
  };

  return (
    <div>
      <h1>Enviar Queja o Petición</h1>
      {message && <p>{message}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="title">Título:</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="description">Descripción:</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          ></textarea>
        </div>
        <button type="submit">Enviar</button>
      </form>
    </div>
  );
};

export default ComplaintForm;
