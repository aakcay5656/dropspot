import { useEffect } from 'react';
import { useDropStore } from '../store/dropStore';
import DropCard from '../components/Drops/DropCard';

export default function DropsPage() {
  const { drops, isLoading, error, fetchDrops } = useDropStore();

  useEffect(() => {
    fetchDrops();
  }, []);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading drops...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Active Drops</h1>
        <p className="text-gray-600">Join waitlists and claim limited items</p>
      </div>

      {drops.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No active drops at the moment</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {drops.map((drop) => (
            <DropCard key={drop.id} drop={drop} />
          ))}
        </div>
      )}
    </div>
  );
}
