import React, { useEffect, useState } from "react";
import axios from "axios";

const UserRoleManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRole, setSelectedRole] = useState({});
  const [error, setError] = useState("");

  const handleLogout = () => {
    localStorage.removeItem("access"); // Elimina el token de acceso
    localStorage.removeItem("refresh"); // Si tienes un token de refresco
    window.location.href = "/"; // Redirige al usuario al login
  };

  const fetchUsers = async () => {
    const token = localStorage.getItem("access"); // Recupera el token desde localStorage
    if (!token) {
      alert("No tienes un token válido, por favor inicia sesión nuevamente.");
      handleLogout();
      return;
    }

    try {
      const response = await axios.get("http://127.0.0.1:8000/api/auth/users/", {
        headers: {
          Authorization: `Token ${token}`, // Usamos el mismo esquema de autorización
        },
      });
      setUsers(response.data.users);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching users:", err);
      if (err.response && err.response.status === 401) {
        alert("Token inválido o expirado. Por favor, inicia sesión de nuevo.");
        handleLogout(); // Elimina el token y redirige al login
      } else {
        setError("No se pudo cargar la lista de usuarios.");
      }
    }
  };

  const updateRole = async (userId) => {
    const token = localStorage.getItem("access");
    if (!token) {
      alert("No tienes un token válido, por favor inicia sesión nuevamente.");
      handleLogout();
      return;
    }

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/auth/users/${userId}/update-role/`,
        { role: selectedRole[userId] },
        {
          headers: {
            Authorization: `Token ${token}`,
          },
        }
      );
      alert(response.data.message);
      fetchUsers(); // Actualiza la lista de usuarios
    } catch (err) {
      console.error("Error updating role:", err);
      if (err.response && err.response.status === 401) {
        alert("Token inválido o expirado. Por favor, inicia sesión de nuevo.");
        handleLogout();
      } else {
        alert("No se pudo actualizar el rol.");
      }
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="user-role-management">
      <h1>Gestión de Roles de Usuarios</h1>
      {error && <p className="text-red-500">{error}</p>}
      <table className="min-w-full table-auto">
        <thead>
          <tr>
            <th>Nombre de Usuario</th>
            <th>Correo</th>
            <th>Rol Actual</th>
            <th>Nuevo Rol</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td>{user.groups__name || "Sin rol"}</td>
              <td>
                <select
                  value={selectedRole[user.id] || ""}
                  onChange={(e) =>
                    setSelectedRole({ ...selectedRole, [user.id]: e.target.value })
                  }
                >
                  <option value="">Seleccionar Rol</option>
                  <option value="admin">Administrador</option>
                  <option value="agent">Agente</option>
                </select>
              </td>
              <td>
                <button
                  onClick={() => updateRole(user.id)}
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  Actualizar Rol
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserRoleManagement;
