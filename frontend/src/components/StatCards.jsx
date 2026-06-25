/**
 * StatCards
 * ---------
 * Renders the six summary cards at the top of the dashboard:
 * Total Leads, Emails Sent, Emails Opened, Open Rate %, Link Clicks, Click Rate %.
 */
export default function StatCards({ stats }) {
  const cards = [
    { label: "Total Leads", value: stats.total_leads, accent: "bg-primary-50 text-primary-700" },
    { label: "Emails Sent", value: stats.emails_sent, accent: "bg-blue-50 text-blue-700" },
    { label: "Emails Opened", value: stats.emails_opened, accent: "bg-amber-50 text-amber-700" },
    { label: "Open Rate", value: `${stats.open_rate}%`, accent: "bg-emerald-50 text-emerald-700" },
    { label: "Link Clicks", value: stats.link_clicks, accent: "bg-purple-50 text-purple-700" },
    { label: "Click Rate", value: `${stats.click_rate}%`, accent: "bg-rose-50 text-rose-700" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex flex-col gap-2"
        >
          <span className={`inline-block self-start text-xs font-medium px-2 py-1 rounded-md ${card.accent}`}>
            {card.label}
          </span>
          <span className="text-2xl font-semibold text-gray-900">{card.value}</span>
        </div>
      ))}
    </div>
  );
}
