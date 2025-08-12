import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from './common/LoadingSpinner';
import Alert from './common/Alert';

const Layout = ({ children }) => {
  const { user, isAuthenticated, logout, loading, hasRole } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [alert, setAlert] = useState(null);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
      setAlert({ type: 'success', message: 'Logged out successfully' });
    } catch (error) {
      setAlert({ type: 'error', message: 'Error logging out' });
    }
  };

  const isActivePath = (path) => {
    return location.pathname === path;
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', roles: ['admin'] },
    { path: '/complaints', label: 'Complaints', roles: ['admin', 'agent', 'user'] },
    { path: '/my-complaints', label: 'My Complaints', roles: ['user'] },
    { path: '/agent-complaints', label: 'Assigned', roles: ['agent'] },
    { path: '/omnichannel', label: 'Omnichannel', roles: ['admin', 'agent'] },
    { path: '/users', label: 'User Management', roles: ['admin'] },
    { path: '/profile', label: 'Profile', roles: ['admin', 'agent', 'user'] },
  ];

  const visibleNavItems = navItems.filter(item => {
    if (!item.roles) return true;
    return item.roles.some(role => hasRole(role));
  });

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo and main nav */}
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link to="/" className="text-xl font-bold text-blue-600">
                  CRM Complaints
                </Link>
              </div>
              
              {isAuthenticated && (
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  {visibleNavItems.map((item) => (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200 ${
                        isActivePath(item.path)
                          ? 'border-blue-500 text-gray-900'
                          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                    >
                      {item.label}
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* User menu */}
            <div className="flex items-center">
              {isAuthenticated ? (
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-700">
                    Welcome, {user?.first_name || user?.username}
                  </span>
                  {user?.groups && user.groups.length > 0 && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {user.groups[0]}
                    </span>
                  )}
                  <button
                    onClick={handleLogout}
                    className="text-gray-500 hover:text-gray-700 text-sm font-medium transition-colors duration-200"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <div className="flex items-center space-x-4">
                  <Link
                    to="/pqrs"
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors duration-200"
                  >
                    Formulario PQRS
                  </Link>
                  <Link
                    to="/login"
                    className="text-gray-500 hover:text-gray-700 text-sm font-medium transition-colors duration-200"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                  >
                    Register
                  </Link>
                </div>
              )}

              {/* Mobile menu button */}
              <div className="ml-6 sm:hidden">
                <button
                  onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                  className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                >
                  <svg
                    className={`${isMobileMenuOpen ? 'hidden' : 'block'} h-6 w-6`}
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                  <svg
                    className={`${isMobileMenuOpen ? 'block' : 'hidden'} h-6 w-6`}
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {isMobileMenuOpen && isAuthenticated && (
          <div className="sm:hidden">
            <div className="pt-2 pb-3 space-y-1">
              {visibleNavItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200 ${
                    isActivePath(item.path)
                      ? 'bg-blue-50 border-blue-500 text-blue-700'
                      : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700'
                  }`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* Alert */}
      {alert && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        </div>
      )}

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-500">
            © 2024 CRM Complaints System. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;