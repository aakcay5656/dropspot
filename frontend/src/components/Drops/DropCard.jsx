import { Link } from 'react-router-dom';
import { useDropStore } from '../../store/dropStore';
import { useAuthStore } from '../../store/authStore';

export default function DropCard({ drop }) {
  const { joinWaitlist, leaveWaitlist } = useDropStore();
  const { token } = useAuthStore();

  const isClaimWindowOpen = () => {
    const now = new Date();
    const start = new Date(drop.claim_window_start);
    const end = new Date(drop.claim_window_end);
    return now >= start && now <= end;
  };

  const getStatus = () => {
    const now = new Date();
    const start = new Date(drop.claim_window_start);
    const end = new Date(drop.claim_window_end);

    if (now < start) return { text: 'Upcoming', color: 'bg-blue-500' };
    if (now >= start && now <= end) return { text: 'Live Now', color: 'bg-green-500' };
    return { text: 'Ended', color: 'bg-gray-500' };
  };

  const handleJoinLeave = async (e) => {
    e.preventDefault();
    try {
      if (drop.user_joined) {
        await leaveWaitlist(drop.id);
        alert('Left waitlist successfully');
      } else {
        const result = await joinWaitlist(drop.id);
        alert(`Joined! Position: ${result.position}`);
      }
    } catch (error) {
      alert(error.response?.data?.detail || 'Action failed');
    }
  };

  const status = getStatus();
  const stockPercentage = (drop.claimed_count / drop.total_stock) * 100;

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow p-6">
      {/* Status Badge */}
      <div className="flex justify-between items-start mb-4">
        <span className={`${status.color} text-white text-xs font-bold px-3 py-1 rounded-full`}>
          {status.text}
        </span>
        {drop.user_joined && (
          <span className="bg-purple-500 text-white text-xs font-bold px-3 py-1 rounded-full">
            Joined
          </span>
        )}
      </div>

      {/* Drop Info */}
      <h3 className="text-xl font-bold text-gray-800 mb-2">{drop.name}</h3>
      <p className="text-gray-600 text-sm mb-4 line-clamp-2">{drop.description}</p>

      {/* Stock Info */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Stock</span>
          <span>{drop.claimed_count} / {drop.total_stock}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${stockPercentage}%` }}
          />
        </div>
      </div>

      {/* Claim Window */}
      <div className="text-xs text-gray-500 mb-4">
        <p>Claim: {new Date(drop.claim_window_start).toLocaleString()}</p>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Link
          to={`/drops/${drop.id}`}
          className="flex-1 bg-gray-800 hover:bg-gray-900 text-white text-center py-2 rounded font-semibold transition"
        >
          View Details
        </Link>

        {token && (
          <button
            onClick={handleJoinLeave}
            className={`flex-1 py-2 rounded font-semibold transition ${
              drop.user_joined
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {drop.user_joined ? 'Leave' : 'Join Waitlist'}
          </button>
        )}
      </div>
    </div>
  );
}
