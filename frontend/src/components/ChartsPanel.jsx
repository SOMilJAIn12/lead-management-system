import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const CATEGORY_COLORS = ["#4f46e5", "#0ea5e9", "#f59e0b", "#10b981", "#ec4899", "#94a3b8"];
const PRIORITY_COLORS = { High: "#ef4444", Medium: "#f59e0b", Low: "#10b981" };

/**
 * ChartsPanel
 * -----------
 * Optional Recharts visualizations:
 *   - Bar chart: lead funnel (Sent -> Opened -> Clicked)
 *   - Pie chart: leads by AI-classified category
 *   - Pie chart: leads by priority
 */
export default function ChartsPanel({ stats }) {
  const funnelData = [
    { stage: "Sent", count: stats.emails_sent },
    { stage: "Opened", count: stats.emails_opened },
    { stage: "Clicked", count: stats.link_clicks },
  ];

  const categoryData = Object.entries(stats.category_breakdown || {}).map(([name, value]) => ({
    name,
    value,
  }));

  const priorityData = Object.entries(stats.priority_breakdown || {}).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <ChartCard title="Email Engagement Funnel">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={funnelData}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="stage" tick={{ fontSize: 12 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="count" fill="#4f46e5" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Leads by Category">
        {categoryData.length === 0 ? (
          <EmptyState />
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={categoryData} dataKey="value" nameKey="name" outerRadius={80} label>
                {categoryData.map((_, i) => (
                  <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        )}
      </ChartCard>

      <ChartCard title="Leads by Priority">
        {priorityData.length === 0 ? (
          <EmptyState />
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={priorityData} dataKey="value" nameKey="name" outerRadius={80} label>
                {priorityData.map((entry, i) => (
                  <Cell key={i} fill={PRIORITY_COLORS[entry.name] || "#94a3b8"} />
                ))}
              </Pie>
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        )}
      </ChartCard>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-2">{title}</h3>
      {children}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="h-[220px] flex items-center justify-center text-sm text-gray-400">
      No data yet
    </div>
  );
}
