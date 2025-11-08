import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Navbar from './components/Layout/Navbar';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DropsPage from './pages/DropsPage';
import DropDetailPage from './pages/DropDetailPage';
import AdminPage from './pages/AdminPage';

function App() {
  const { token, user } = useAuthStore();

  const ProtectedRoute = ({ children, adminOnly = false }) => {
    if (!token) return <Navigate to="/login" />;
    if (adminOnly && user?.role !== 'admin') return <Navigate to="/" />;
    return children;
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route
            path="/login"
            element={!token ? <LoginPage /> : <Navigate to="/" />}
          />
          <Route
            path="/signup"
            element={!token ? <SignupPage /> : <Navigate to="/" />}
          />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DropsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/drops/:id"
            element={
              <ProtectedRoute>
                <DropDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute adminOnly>
                <AdminPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
