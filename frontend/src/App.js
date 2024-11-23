import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Login from "./components/auth/Login";
import Register from "./components/auth/Register";
import UsersList from "./components/auth/UsersList";
import Dashboard from './components/Dashboard'; // Asegúrate de que el archivo Dashboard.js exista en esta ruta
import ComplaintForm from "./components/ComplaintForm"; // Importa el componente

function App() {
  return (
    <Router>      
        <Routes>          
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/users" element={<UsersList />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/complaint-form" element={<ComplaintForm />} />
        </Routes>      
    </Router>
  );
}

export default App;
