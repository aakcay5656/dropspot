export default function DropTable({ drops, onEdit, onDelete }) {
  const getStatusBadge = (drop) => {
    const now = new Date();
    const start = new Date(drop.claim_window_start);
    const end = new Date(drop.claim_window_end);

    if (now < start) {
      return <span className="bg-blue-500 text-white px-2 py-1 rounded text-xs">Upcoming</span>;
    }
    if (now >= start && now <= end) {
      return <span className="bg-green-500 text-white px-2 py-1 rounded text-xs">Live</span>;
    }
    return <span className="bg-gray-500 text-white px-2 py-1 rounded text-xs">Ended</span>;
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stock</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Claim Start</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {drops.length === 0 ? (
            <tr>
              <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                No drops found
              </td>
            </tr>
          ) : (
            drops.map((drop) => (
              <tr key={drop.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-900">{drop.id}</td>
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">{drop.name}</div>
                  <div className="text-sm text-gray-500 truncate max-w-xs">{drop.description}</div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  {drop.claimed_count} / {drop.total_stock}
                </td>
                <td className="px-6 py-4">{getStatusBadge(drop)}</td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  {new Date(drop.claim_window_start).toLocaleString()}
                </td>
                <td className="px-6 py-4 text-right text-sm font-medium">
                  <button
                    onClick={() => onEdit(drop)}
                    className="text-blue-600 hover:text-blue-900 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(drop.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
