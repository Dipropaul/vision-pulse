'use client';

import { Video, videoApi } from '@/lib/api';
import { Download, Trash2, Clock, CheckCircle, XCircle, Loader, RefreshCw } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface VideoGalleryProps {
  videos: Video[];
  onUpdate: () => void;
}

export default function VideoGallery({ videos, onUpdate }: VideoGalleryProps) {
  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this video?')) {
      try {
        await videoApi.deleteVideo(id);
        onUpdate();
      } catch (error) {
        console.error('Failed to delete video:', error);
        alert('Failed to delete video');
      }
    }
  };

  const handleRegenerate = async (id: string) => {
    if (confirm('Regenerate this video with the same settings?')) {
      try {
        await videoApi.regenerateVideo(id);
        onUpdate();
      } catch (error) {
        console.error('Failed to regenerate video:', error);
        alert('Failed to regenerate video');
      }
    }
  };

  const handleDownload = (videoPath: string, title: string) => {
    const url = videoApi.getVideoUrl(videoPath);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title}.mp4`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'processing':
      case 'pending':
        return <Loader className="w-5 h-5 text-yellow-400 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'processing':
        return 'Processing';
      case 'pending':
        return 'Pending';
      case 'failed':
        return 'Failed';
      default:
        return status;
    }
  };

  if (videos.length === 0) {
    return (
      <div className="text-center py-20">
        <div className="text-gray-400 text-lg mb-2">No videos yet</div>
        <div className="text-gray-500">Click "Create New Video" to get started</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {videos.map((video) => (
        <div
          key={video.id}
          className="bg-white/10 backdrop-blur-lg rounded-lg overflow-hidden border border-white/20 hover:border-purple-400 transition-all"
        >
          {/* Video Preview */}
          {video.status === 'completed' && video.video_path ? (
            <div className="relative aspect-video bg-black">
              <video
                src={videoApi.getVideoUrl(video.video_path)}
                controls
                className="w-full h-full"
              />
            </div>
          ) : (
            <div className="relative aspect-video bg-gradient-to-br from-purple-900/50 to-blue-900/50 flex items-center justify-center">
              {getStatusIcon(video.status)}
            </div>
          )}

          {/* Video Info */}
          <div className="p-4">
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-white font-semibold text-lg line-clamp-1">
                {video.title}
              </h3>
              <div className="flex items-center gap-1 text-sm">
                {getStatusIcon(video.status)}
              </div>
            </div>

            <p className="text-gray-400 text-sm line-clamp-2 mb-3">
              {video.script}
            </p>

            <div className="flex items-center gap-2 mb-3 flex-wrap">
              <span className="px-2 py-1 bg-purple-500/30 text-purple-300 text-xs rounded">
                {video.style}
              </span>
              <span className="px-2 py-1 bg-blue-500/30 text-blue-300 text-xs rounded">
                {video.voice}
              </span>
              {video.duration && (
                <span className="px-2 py-1 bg-green-500/30 text-green-300 text-xs rounded">
                  {Math.floor(video.duration / 60)}:{(video.duration % 60).toString().padStart(2, '0')}
                </span>
              )}
              <span className="px-2 py-1 bg-gray-500/30 text-gray-300 text-xs rounded">
                {getStatusText(video.status)}
              </span>
            </div>

            {video.created_at && (
              <p className="text-gray-500 text-xs mb-3">
                {formatDistanceToNow(new Date(video.created_at), { addSuffix: true })}
              </p>
            )}

            {video.error_message && (
              <div className="bg-red-500/20 border border-red-500 rounded p-2 mb-3">
                <p className="text-red-300 text-xs">{video.error_message}</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2">
              {video.status === 'completed' && video.video_path && (
                <button
                  onClick={() => handleDownload(video.video_path!, video.title)}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Download
                </button>
              )}
              <button
                onClick={() => handleRegenerate(video.id)}
                className="flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                title="Regenerate with same settings"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleDelete(video.id)}
                className="flex items-center justify-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
