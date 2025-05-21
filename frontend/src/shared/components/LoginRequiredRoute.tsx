import React from "react";
import { Navigate } from "react-router-dom";

interface LoginRequiredProps {
  isAuthenticated: boolean;
  children: React.ReactNode;
}

const LoginRequired: React.FC<LoginRequiredProps> = ({ isAuthenticated, children }) => {
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export default LoginRequired;