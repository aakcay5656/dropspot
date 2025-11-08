import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDropStore } from '../store/dropStore';
import { useAuthStore } from '../store/authStore';

export default function DropDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { selectedDrop, isLoading, fetchDrop, joinWaitlist, leaveWaitlist, claimDrop } = useDropStore();
  const { token } = useAuthStore();
  const [claimCode, setClaimCode] = useState(null);
  const [showClaimModal, setShowClaimModal] = useState(false);

  useEffect(() => {
    fetchDrop(id);
  }, [id]);

  if (isLoading || !selectedDrop) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
        </div>
      </div>
    );
  }

  const drop = selectedDrop;

  const isClaimWindowOpen = () => {
    const now = new Date();
    const start = new Date(drop.claim_window_start);
    const end = new Date(drop.claim_window_end);
    return now >= start && now <= end;
  };

  const handleJoinLeave = async () => {
    try {
      if (drop.user_joined) {
        await leaveWaitlist(drop.id);
        alert('Left waitlist successfully');
        fetchDrop(id);
      } else {
        const result = await joinWaitlist(drop.id);
        alert(`Joined! Position: ${result.position}, Priority Score: ${result.priority_score.toFixed(2)}`);
        fetchDrop(id);
      }
    } catch (error) {
      alert(error.response?.data?.detail || 'Action failed');
    }
  };

  const handleClaim = async () => {
    try {
      const result = await claimDrop(drop.id);
      setClaimCode(result.claim_code);
      setShowClaimModal(true);
    } catch (error) {
      alert(error.response?.data?.detail || 'Claim failed');
    }
  };

  const stockPercentage = (drop.claimed_count / drop.total_stock) * 100;
  const canClaim = drop.user_joined && isClaimWindowOpen();

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Back Button */}
      <button
        onClick={() => navigate('/')}
        className="mb-6 text-blue-600 hover:text-blue-800 flex items-center gap-2"
      >
        ← Back to Drops
      </button>

      <div className="bg-white rounded-lg shadow-lg p-8">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">{drop.name}</h1>
            <p className="text-gray-600">{drop.description}</p>
          </div>
          {drop.user_joined && (
            <span className="bg-purple-500 text-white px-4 py-2 rounded-full font-semibold">
              Joined
            </span>
          )}
        </div>

        {/* Stock Progress */}
        <div className="mb-6">
          <div className="flex justify-between text-lg font-semibold text-gray-700 mb-2">
            <span>Stock Available</span>
            <span>{drop.total_stock - drop.claimed_count} / {drop.total_stock}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-blue-600 h-4 rounded-full transition-all"
              style={{ width: `${stockPercentage}%` }}
            />
          </div>
        </div>

        {/* Claim Window */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-gray-700 mb-2">Claim Window</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Start</p>
              <p className="font-semibold">{new Date(drop.claim_window_start).toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">End</p>
              <p className="font-semibold">{new Date(drop.claim_window_end).toLocaleString()}</p>
            </div>
          </div>
          <div className="mt-3">
            {isClaimWindowOpen() ? (
              <span className="inline-block bg-green-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                ✓ Live Now
              </span>
            ) : new Date() < new Date(drop.claim_window_start) ? (
              <span className="inline-block bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                Upcoming
              </span>
            ) : (
              <span className="inline-block bg-gray-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                Ended
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        {token && (
          <div className="flex gap-4">
            <button
              onClick={handleJoinLeave}
              className={`flex-1 py-3 rounded-lg font-semibold transition ${
                drop.user_joined
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              {drop.user_joined ? 'Leave Waitlist' : 'Join Waitlist'}
            </button>

            {canClaim && (
              <button
                onClick={handleClaim}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-semibold transition"
              >
                Claim Now
              </button>
            )}
          </div>
        )}
      </div>

      {/* Claim Code Modal */}
      {showClaimModal && claimCode && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-green-600 mb-4">✓ Claim Successful!</h2>
            <p className="text-gray-600 mb-4">Your unique claim code:</p>
            <div className="bg-gray-100 p-4 rounded-lg mb-6">
              <p className="text-2xl font-mono font-bold text-center text-gray-800">{claimCode}</p>
            </div>
            <p className="text-sm text-gray-500 mb-6">
              Save this code! It expires in 24 hours.
            </p>
            <button
              onClick={() => {
                setShowClaimModal(false);
                navigate('/');
              }}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
