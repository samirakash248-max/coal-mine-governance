import { Link } from 'react-router-dom';
import { useMines } from '../../hooks/useMines';

import { Loader2, Inbox } from 'lucide-react';

export default function MineList() {
  const { data: mines, isLoading } = useMines();

  if (isLoading) return (
    <div className="p-6 flex justify-center items-center h-64 text-gray-500">
      <Loader2 className="w-8 h-8 animate-spin" />
    </div>
  );

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Mines</h1>
      
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {mines && mines.length === 0 ? (
          <div className="p-12 text-center flex flex-col items-center">
            <Inbox className="w-12 h-12 text-gray-400 mb-3" />
            <h3 className="text-lg font-medium text-gray-900">No Mines Found</h3>
            <p className="text-gray-500 mt-1">There are currently no mines to display.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-500 uppercase bg-gray-50">
                <tr>
                  <th className="px-6 py-3">Name</th>
                  <th className="px-6 py-3">Location</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {mines?.map(mine => (
                <tr key={mine.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">{mine.name}</td>
                  <td className="px-6 py-4">{mine.location}</td>
                  <td className="px-6 py-4">{mine.status}</td>
                  <td className="px-6 py-4">
                    <Link to={`/mines/${mine.id}`} className="text-mining-amber-600 hover:underline font-medium">
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        )}
      </div>
    </div>
  );
}
