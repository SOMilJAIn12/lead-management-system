import { useEffect, useState, useCallback } from "react";
import { fetchDashboard } from "../services/api";
import StatCards from "../components/StatCards";
import ChartsPanel from "../components/ChartsPanel";
import LeadsTable from "../components/LeadsTable";

/**
 * DashboardPage
 * -------------
 * Top-level dashboard: summary cards, charts, and the searchable leads table.
 * Polls /dashboard periodically so the cards stay roughly fresh as new leads
 * come in or emails get opened/clicked.
 */
export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  const loadStats = useCallback(async () => {
    try {
      const data = await fetchDashboard();
      setStats(data);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 15000); // refresh every 15s
    return () => clearInterval(interval);
  }, [loadStats]);

  return (
    <div className="py-8 px-4 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Lead Dashboard</h1>
        <p className="text-gray-500 text-sm">Track lead capture, email engagement, and AI classification.</p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {!stats && !error && <p className="text-gray-400 text-sm">Loading dashboard...</p>}

      {stats && (
        <>
          <StatCards stats={stats} />
          <ChartsPanel stats={stats} />
        </>
      )}

      <LeadsTable />
    </div>
  );
}
