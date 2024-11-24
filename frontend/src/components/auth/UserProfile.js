import React, { useEffect, useState } from "react";
import axios from "axios";

const UserProfile = () => {
  const [userData, setUserData] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
  });
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    window.location.href = "/";
  };

  const fetchUserProfile = async () => {
    const token = localStorage.getItem("access");
    if (!token) {
      alert("No tienes un token válido, por favor inicia sesión nuevamente.");
      handleLogout();
      return;
    }

    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/auth/profile/",
        {
          headers: {
            Authorization: `Token ${token}`,
          },
        }
      );
      setUserData(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching user profile:", error);
      if (error.response && error.response.status === 401) {
        alert("Token inválido o expirado. Por favor, inicia sesión de nuevo.");
        handleLogout();
      }
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("access");
    if (!token) {
      alert("No tienes un token válido, por favor inicia sesión nuevamente.");
      handleLogout();
      return;
    }

    try {
      const response = await axios.put(
        "http://127.0.0.1:8000/api/auth/profile/",
        userData,
        {
          headers: {
            Authorization: `Token ${token}`,
          },
        }
      );
      setMessage(response.data.message);
    } catch (error) {
      console.error("Error updating user profile:", error);
      alert("No se pudo actualizar el perfil.");
    }
  };

  useEffect(() => {
    fetchUserProfile();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="user-profile">
      <h1>Editar Perfil</h1>
      {message && <p className="text-green-500">{message}</p>}
      <form onSubmit={handleUpdate}>
        <div>
          <label>Nombre:</label>
          <input
            type="text"
            value={userData.first_name}
            onChange={(e) =>
              setUserData({ ...userData, first_name: e.target.value })
            }
          />
        </div>
        <div>
          <label>Apellido:</label>
          <input
            type="text"
            value={userData.last_name}
            onChange={(e) =>
              setUserData({ ...userData, last_name: e.target.value })
            }
          />
        </div>
        <div>
          <label>Correo:</label>
          <input
            type="email"
            value={userData.email}
            onChange={(e) =>
              setUserData({ ...userData, email: e.target.value })
            }
          />
        </div>
        <div>
          <label>Contraseña:</label>
          <input
            type="password"
            placeholder="Dejar en blanco para no cambiar"
            onChange={(e) =>
              setUserData({ ...userData, password: e.target.value })
            }
          />
        </div>
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Actualizar
        </button>
      </form>
    </div>
  );
};

export default UserProfile;
