import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useDropStore } from '../store/dropStore';
import { useAdminStore } from '../store/adminStore';
import DropForm from '../components/Admin/DropForm';
import DropTable from '../components/Admin/DropTable';

export default function AdminPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { drops, fetchDrops } = useDropStore();
  const { createDrop, updateDrop, deleteDrop, isLoading } = useAdminStore();

  const [showForm, setShowForm] = useState(false);
  const [editingDrop, setEditingDrop] = useState(null);

  useEffect(() => {
    // Admin kontrolü
    if (!user || user.role !== 'admin') {
      navigate('/');
      return;
    }
    fetchDrops();
  }, [user]);

  const handleCreate = () => {
    setEditingDrop(null);
    setShowForm(true);
  };

  const handleEdit = (drop) => {
    setEditingDrop(drop);
    setShowForm(true);
  };

  const handleSubmit = async (data) => {
    try {
      if (editingDrop) {
        await updateDrop(editingDrop.id, data);
        alert('Drop updated successfully');
      } else {
        await createDrop(data);
        alert('Drop created successfully');
      }
      setShowForm(false);
      setEditingDrop(null);
      fetchDrops();
    } catch (error) {
      alert(error.response?.data?.detail || 'Operation failed');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this drop?')) {
      return;
    }

    try {
      await deleteDrop(id);
      alert('Drop deleted successfully');
      fetchDrops();
    } catch (error) {
      alert(error.response?.data?.detail || 'Delete failed');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingDrop(null);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">Admin Panel</h1>
            <p className="text-gray-600">Manage drops and inventory</p>
          </div>
          <button
            onClick={handleCreate}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold"
          >
            + Create New Drop
          </button>
        </div>
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">
              {editingDrop ? 'Edit Drop' : 'Create New Drop'}
            </h2>
            <DropForm
              initialData={editingDrop}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              isLoading={isLoading}
            />
          </div>
        </div>
      )}

      {/* Drops Table */}
      <div className="bg-white rounded-lg shadow">
        <DropTable
          drops={drops}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium mb-2">Total Drops</h3>
          <p className="text-3xl font-bold text-gray-800">{drops.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium mb-2">Total Stock</h3>
          <p className="text-3xl font-bold text-gray-800">
            {drops.reduce((sum, drop) => sum + drop.total_stock, 0)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium mb-2">Total Claims</h3>
          <p className="text-3xl font-bold text-gray-800">
            {drops.reduce((sum, drop) => sum + drop.claimed_count, 0)}
          </p>
        </div>
      </div>
    </div>
  );
}
