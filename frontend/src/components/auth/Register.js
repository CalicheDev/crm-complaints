import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setErrorMessage("Las contraseñas no coinciden.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          password,
          email,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert("Registro exitoso. Ahora puedes iniciar sesión.");
        navigate("/");
      } else {
        setErrorMessage(data.error || "Ocurrió un error durante el registro.");
      }
    } catch (error) {
      setErrorMessage("Error al conectar con el servidor.");
      console.error("Error:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <form
        onSubmit={handleRegister}
        className="bg-white p-6 rounded shadow-md space-y-4 w-96"
      >
        <h1 className="text-2xl font-bold text-center">Regístrate</h1>
        {errorMessage && (
          <div className="text-red-500 text-sm">{errorMessage}</div>
        )}
        <input
          type="text"
          placeholder="Nombre de usuario"
          className="w-full p-2 border rounded"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Correo"
          className="w-full p-2 border rounded"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Contraseña"
          className="w-full p-2 border rounded"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Confirmar Contraseña"
          className="w-full p-2 border rounded"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
        <button
          type="submit"
          className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        >
          Registrarse
        </button>
        <p className="text-sm text-gray-600 text-center">
          ¿Ya tienes cuenta?{" "}
          <a href="/" className="text-blue-500 hover:underline">
            Inicia sesión
          </a>
        </p>
      </form>
    </div>
  );
}

export default Register;
