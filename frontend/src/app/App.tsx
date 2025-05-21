import { useEffect } from "react";
import { BrowserRouter as Router } from 'react-router-dom';
import Topbar from "../shared/components/Topbar";
import Toast from "../shared/components/Toast";
import Footer from "../shared/components/Footer";
import AppRoutes from "../routes/AppRoutes";
import { AuthProvider, useAuth } from '../shared/context/AuthContext';
import './App.css';

function App() {
  // Use auth context
  const { accessToken, userEmail, isAuthenticated, setAccessToken, setUserEmail, handleLogout, ws } = useAuth();

  useEffect(() => {
    if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
      Notification.requestPermission().then(permission => {
        if (permission === "granted") {
          console.log("Browser notification permission granted.");
        }
      });
    }
  }, []);

  return (
    <div className="app-container">
      <Topbar/>
      <AppRoutes isAuthenticated={isAuthenticated} />
      <Footer />
      <Toast />
    </div>
  );
}


function AppWithProviders() {
  return (
    <Router>
      <AuthProvider>
        <App />
      </AuthProvider>
    </Router>
  );
}

export default AppWithProviders;