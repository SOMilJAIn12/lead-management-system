import { NavLink, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import DashboardPage from "./pages/DashboardPage";

/** Top-level app: nav bar + routed pages. */
export default function App() {
  return (
    <div className="min-h-screen">
      <nav className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <span className="font-semibold text-gray-900">Lead Management System</span>
          <div className="flex gap-2">
            <NavTab to="/">Lead Form</NavTab>
            <NavTab to="/dashboard">Dashboard</NavTab>
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </div>
  );
}

function NavTab({ to, children }) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
          isActive ? "bg-primary-50 text-primary-700" : "text-gray-600 hover:bg-gray-50"
        }`
      }
    >
      {children}
    </NavLink>
  );
}
