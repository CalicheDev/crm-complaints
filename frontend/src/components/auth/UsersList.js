import React, { useEffect, useState } from "react";
import axios from "axios";

const UserRoleManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRole, setSelectedRole] = useState({});
  const [error, setError] = useState("");

  const fetchUsers = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/auth/users/", {
        headers: {
          Authorization: `Token ${localStorage.getItem("authToken")}`,
        },
      });
      setUsers(response.data.users);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching users:", err);
      setError("No se pudo cargar la lista de usuarios.");
    }
  };

  const updateRole = async (userId) => {
    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/auth/users/${userId}/update-role/`,
        { role: selectedRole[userId] },
        {
          headers: {
            Authorization: `Token ${localStorage.getItem("authToken")}`,
          },
        }
      );
      alert(response.data.message);
      fetchUsers(); // Refresh user list
    } catch (err) {
      console.error("Error updating role:", err);
      alert("No se pudo actualizar el rol.");
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
