import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard'; // Asegúrate de que el archivo Dashboard.js exista en esta ruta
import ComplaintForm from "./components/ComplaintForm"; // Importa el componente

function App() {
  return (
    <Router>
      <div className="App">
        <nav>
          <Link to="/">Inicio</Link> | <Link to="/dashboard">Dashboard</Link> |{" "}
          <Link to="/complaint-form">Enviar Queja</Link>
        </nav>
        <Routes>
          <Route path="/" element={<h1>Bienvenido al CRM</h1>} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/complaint-form" element={<ComplaintForm />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
