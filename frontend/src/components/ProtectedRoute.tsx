import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute: React.FC = () => {
  const { isLoggedIn, isLoading } = useAuth();
  const location = useLocation();
  
  if (isLoading) {
    return <div className="text-center p-5">Loading authentication...</div>;
  }
  
  if (!isLoggedIn) {
    // Redirect to login but save the current location
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  // If authenticated, render the child routes
  return <Outlet />;
};

export default ProtectedRoute;