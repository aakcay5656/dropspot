import { useState, useEffect } from 'react';

export default function DropForm({ initialData, onSubmit, onCancel, isLoading }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    total_stock: '',
    claim_window_start: '',
    claim_window_end: '',
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || '',
        description: initialData.description || '',
        total_stock: initialData.total_stock || '',
        claim_window_start: initialData.claim_window_start?.slice(0, 16) || '',
        claim_window_end: initialData.claim_window_end?.slice(0, 16) || '',
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Convert datetime-local to ISO format
    const submitData = {
      ...formData,
      total_stock: parseInt(formData.total_stock),
      claim_window_start: new Date(formData.claim_window_start).toISOString(),
      claim_window_end: new Date(formData.claim_window_end).toISOString(),
    };

    onSubmit(submitData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Drop Name *
        </label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          placeholder="Nike Air Force 1"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          placeholder="Limited edition sneakers..."
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Total Stock *
        </label>
        <input
          type="number"
          name="total_stock"
          value={formData.total_stock}
          onChange={handleChange}
          required
          min="1"
          className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          placeholder="50"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Claim Window Start *
          </label>
          <input
            type="datetime-local"
            name="claim_window_start"
            value={formData.claim_window_start}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Claim Window End *
          </label>
          <input
            type="datetime-local"
            name="claim_window_end"
            value={formData.claim_window_end}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : initialData ? 'Update Drop' : 'Create Drop'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 py-3 rounded-lg font-semibold"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
