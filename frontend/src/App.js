import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Login from "./components/auth/Login";
import Register from "./components/auth/Register";
import UserRoleManagement from "./components/auth/UserRoleManagement";
import UserProfile from "./components/auth/UserProfile";
import Dashboard from './components/Dashboard'; // Asegúrate de que el archivo Dashboard.js exista en esta ruta
import ComplaintForm from "./components/ComplaintForm"; // Importa el componente


function App() {
  return (
    <Router>      
        <Routes>          
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/users" element={<UserRoleManagement />} />
          <Route path="/profile" element={<UserProfile />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/complaint-form" element={<ComplaintForm />} />
        </Routes>      
    </Router>
  );
}

export default App;
