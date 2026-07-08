import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

interface ProtectedRouteProps {
  children?: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const token = localStorage.getItem("civiclens_token");
  const location = useLocation();

  if (!token) {
    // If there is no token, redirect to admin page with location state
    return <Navigate to="/admin" state={{ from: location }} replace />;
  }

  // Render children or nested routes via Outlet
  return children ? <>{children}</> : <Outlet />;
}
