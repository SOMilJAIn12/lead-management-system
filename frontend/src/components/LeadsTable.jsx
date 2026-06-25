import { useEffect, useState, useCallback } from "react";
import { fetchLeads } from "../services/api";

/**
 * LeadsTable
 * ----------
 * Searchable table of all captured leads. Search is debounced and sent to
 * the backend (`GET /leads?search=...`) so it works across the full leads
 * collection, not just whatever happens to be loaded on the page.
 */
export default function LeadsTable() {
  const [leads, setLeads] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadLeads = useCallback(async (term) => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchLeads(term);
      setLeads(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadLeads("");
  }, [loadLeads]);

  // Debounce search input so we don't fire a request on every keystroke.
  useEffect(() => {
    const timer = setTimeout(() => {
      loadLeads(search);
    }, 350);
    return () => clearTimeout(timer);
  }, [search, loadLeads]);

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
      <div className="flex items-center justify-between gap-4 p-4 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-700">All Leads</h3>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name, email, company, requirement..."
          className="w-72 rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {error && <p className="px-4 py-3 text-sm text-red-600">{error}</p>}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-100">
              <Th>Name</Th>
              <Th>Email</Th>
              <Th>Phone</Th>
              <Th>Company</Th>
              <Th>Requirement</Th>
              <Th>Category</Th>
              <Th>Priority</Th>
              <Th>Email Opened</Th>
              <Th>Link Clicked</Th>
              <Th>Submitted</Th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={10} className="px-4 py-6 text-center text-gray-400">
                  Loading leads...
                </td>
              </tr>
            )}
            {!loading && leads.length === 0 && (
              <tr>
                <td colSpan={10} className="px-4 py-6 text-center text-gray-400">
                  No leads found.
                </td>
              </tr>
            )}
            {!loading &&
              leads.map((lead) => (
                <tr key={lead.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <Td className="font-medium text-gray-900">{lead.full_name}</Td>
                  <Td>{lead.email}</Td>
                  <Td>{lead.phone}</Td>
                  <Td>{lead.company || "-"}</Td>
                  <Td className="max-w-xs truncate" title={lead.requirement}>
                    {lead.requirement}
                  </Td>
                  <Td>
                    <span className="inline-block px-2 py-0.5 rounded-md bg-gray-100 text-gray-700 text-xs">
                      {lead.category}
                    </span>
                  </Td>
                  <Td>
                    <PriorityBadge priority={lead.priority} />
                  </Td>
                  <Td>
                    <StatusBadge value={lead.email_opened} />
                  </Td>
                  <Td>
                    <StatusBadge value={lead.link_clicked} />
                  </Td>
                  <Td className="whitespace-nowrap text-gray-500">
                    {new Date(lead.submitted_at).toLocaleString()}
                  </Td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Th({ children }) {
  return <th className="px-4 py-2 font-medium whitespace-nowrap">{children}</th>;
}

function Td({ children, className = "" }) {
  return <td className={`px-4 py-2 ${className}`}>{children}</td>;
}

function StatusBadge({ value }) {
  return value ? (
    <span className="inline-flex items-center gap-1 text-emerald-700 text-xs font-medium">
      ● Yes
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 text-gray-400 text-xs font-medium">
      ○ No
    </span>
  );
}

function PriorityBadge({ priority }) {
  const styles = {
    High: "bg-red-50 text-red-700",
    Medium: "bg-amber-50 text-amber-700",
    Low: "bg-green-50 text-green-700",
  };
  return (
    <span className={`inline-block px-2 py-0.5 rounded-md text-xs font-medium ${styles[priority] || "bg-gray-100 text-gray-700"}`}>
      {priority}
    </span>
  );
}
