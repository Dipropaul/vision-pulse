'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { Video, videoApi } from '@/lib/api';
import VideoGallery from '@/components/VideoGallery';
import CreateVideoModal from '@/components/CreateVideoModal';
import { Plus, Film } from 'lucide-react';

const fetcher = () => videoApi.listVideos();

export default function Home() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { data: videos, error, isLoading, mutate } = useSWR<Video[]>('/videos', fetcher, {
    refreshInterval: 3000, // Poll every 3 seconds for status updates
  });

  const handleVideoCreated = () => {
    mutate(); // Refresh the video list
    setIsCreateModalOpen(false);
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Film className="w-10 h-10 text-purple-400" />
              <h1 className="text-4xl font-bold text-white">VisionPulse</h1>
            </div>
            <p className="text-gray-300">Transform scripts into AI-generated videos</p>
          </div>
          
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors shadow-lg hover:shadow-purple-500/50"
          >
            <Plus className="w-5 h-5" />
            Create New Video
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4 border border-white/20">
            <p className="text-gray-400 text-sm">Total Videos</p>
            <p className="text-3xl font-bold text-white">{videos?.length || 0}</p>
          </div>
          <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4 border border-white/20">
            <p className="text-gray-400 text-sm">Completed</p>
            <p className="text-3xl font-bold text-green-400">
              {videos?.filter(v => v.status === 'completed').length || 0}
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4 border border-white/20">
            <p className="text-gray-400 text-sm">Processing</p>
            <p className="text-3xl font-bold text-yellow-400">
              {videos?.filter(v => v.status === 'processing' || v.status === 'pending').length || 0}
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4 border border-white/20">
            <p className="text-gray-400 text-sm">Failed</p>
            <p className="text-3xl font-bold text-red-400">
              {videos?.filter(v => v.status === 'failed').length || 0}
            </p>
          </div>
        </div>

        {/* Video Gallery */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-white text-lg">Loading videos...</div>
          </div>
        ) : error ? (
          <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 text-red-200">
            Error loading videos. Make sure the backend is running.
          </div>
        ) : (
          <VideoGallery videos={videos || []} onUpdate={mutate} />
        )}

        {/* Create Video Modal */}
        {isCreateModalOpen && (
          <CreateVideoModal
            onClose={() => setIsCreateModalOpen(false)}
            onSuccess={handleVideoCreated}
          />
        )}
      </div>
    </main>
  );
}
