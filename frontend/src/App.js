import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/common/ProtectedRoute';

// Import components
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import UserProfile from './components/auth/UserProfile';
import UserRoleManagement from './components/auth/UserRoleManagement';
import Dashboard from './components/Dashboard';
import ComplaintForm from './components/ComplaintForm';
import ComplaintList from './components/ComplaintList';
import ComplaintDetails from './components/ComplaintDetails';
import PublicPQRSForm from './components/PublicPQRSForm';

// Error pages
const NotFound = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">404 - Page Not Found</h1>
      <p className="text-gray-600 mb-8">The page you're looking for doesn't exist.</p>
      <a href="/" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md">
        Go Home
      </a>
    </div>
  </div>
);

const Unauthorized = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">403 - Unauthorized</h1>
      <p className="text-gray-600 mb-8">You don't have permission to access this resource.</p>
      <a href="/dashboard" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md">
        Go to Dashboard
      </a>
    </div>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/pqrs" element={<PublicPQRSForm />} />
            <Route path="/unauthorized" element={<Unauthorized />} />

            {/* Protected routes */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute adminOnly>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <UserProfile />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/users" 
              element={
                <ProtectedRoute adminOnly>
                  <UserRoleManagement />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/complaints" 
              element={
                <ProtectedRoute>
                  <ComplaintList />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/complaints/:id" 
              element={
                <ProtectedRoute>
                  <ComplaintDetails />
                </ProtectedRoute>
              } 
            />
            
            <Route path="/complaint-form" element={<ComplaintForm />} />
            <Route path="/submit-complaint" element={<ComplaintForm />} />
            
            <Route 
              path="/my-complaints" 
              element={
                <ProtectedRoute>
                  <ComplaintList userComplaints />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/agent-complaints" 
              element={
                <ProtectedRoute agentOnly>
                  <ComplaintList agentComplaints />
                </ProtectedRoute>
              } 
            />

            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/pqrs" replace />} />
            
            {/* 404 route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;