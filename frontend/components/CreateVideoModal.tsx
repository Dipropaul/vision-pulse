'use client';

import { useState, useEffect } from 'react';
import { videoApi, Style, Voice, VideoCreateRequest } from '@/lib/api';
import { X, Loader } from 'lucide-react';

interface CreateVideoModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function CreateVideoModal({ onClose, onSuccess }: CreateVideoModalProps) {
  const [formData, setFormData] = useState<VideoCreateRequest>({
    title: '',
    script: '',
    style: '',
    voice: '',
    size: '1280x720',
    duration: 8,
    keywords: [],
    negative_keywords: [],
  });

  const [keywordInput, setKeywordInput] = useState('');
  const [negativeKeywordInput, setNegativeKeywordInput] = useState('');
  const [styles, setStyles] = useState<Style[]>([]);
  const [voices, setVoices] = useState<Voice[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [stylesData, voicesData] = await Promise.all([
          videoApi.listStyles(),
          videoApi.listVoices(),
        ]);
        setStyles(stylesData);
        setVoices(voicesData);
        
        // Set defaults
        if (stylesData.length > 0) {
          setFormData(prev => ({ ...prev, style: stylesData[0].id }));
        }
        if (voicesData.length > 0) {
          setFormData(prev => ({ ...prev, voice: voicesData[0].id }));
        }
      } catch (err) {
        console.error('Failed to fetch options:', err);
        setError('Failed to load options');
      }
    };

    fetchOptions();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await videoApi.createVideo(formData);
      onSuccess();
    } catch (err: any) {
      console.error('Failed to create video:', err);
      setError(err.response?.data?.detail || 'Failed to create video');
    } finally {
      setIsLoading(false);
    }
  };

  const addKeyword = () => {
    if (keywordInput.trim() && formData.keywords) {
      setFormData({
        ...formData,
        keywords: [...formData.keywords, keywordInput.trim()],
      });
      setKeywordInput('');
    }
  };

  const removeKeyword = (index: number) => {
    if (formData.keywords) {
      setFormData({
        ...formData,
        keywords: formData.keywords.filter((_, i) => i !== index),
      });
    }
  };

  const addNegativeKeyword = () => {
    if (negativeKeywordInput.trim() && formData.negative_keywords) {
      setFormData({
        ...formData,
        negative_keywords: [...formData.negative_keywords, negativeKeywordInput.trim()],
      });
      setNegativeKeywordInput('');
    }
  };

  const removeNegativeKeyword = (index: number) => {
    if (formData.negative_keywords) {
      setFormData({
        ...formData,
        negative_keywords: formData.negative_keywords.filter((_, i) => i !== index),
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-slate-900 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto border border-purple-500/30">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <h2 className="text-2xl font-bold text-white">Create New Video</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-500/20 border border-red-500 rounded-lg p-3 text-red-200">
              {error}
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-white font-medium mb-2">
              Video Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
              placeholder="My Awesome Video"
              required
            />
          </div>

          {/* Script */}
          <div>
            <label className="block text-white font-medium mb-2">
              Script *
            </label>
            <textarea
              value={formData.script}
              onChange={(e) => setFormData({ ...formData, script: e.target.value })}
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 h-32"
              placeholder="Enter your video script here..."
              required
            />
            <p className="text-gray-400 text-sm mt-1">
              This will be used for narration and to generate visual prompts
            </p>
          </div>

          {/* Style */}
          <div>
            <label className="block text-white font-medium mb-2">
              Visual Style *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {styles.map((style) => (
                <button
                  key={style.id}
                  type="button"
                  onClick={() => setFormData({ ...formData, style: style.id })}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    formData.style === style.id
                      ? 'border-purple-500 bg-purple-500/20'
                      : 'border-white/20 bg-white/5 hover:border-white/40'
                  }`}
                >
                  <div className="text-white font-medium text-sm">{style.name}</div>
                  <div className="text-gray-400 text-xs mt-1">{style.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Voice */}
          <div>
            <label className="block text-white font-medium mb-2">
              Narration Voice *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {voices.map((voice) => (
                <button
                  key={voice.id}
                  type="button"
                  onClick={() => setFormData({ ...formData, voice: voice.id })}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    formData.voice === voice.id
                      ? 'border-blue-500 bg-blue-500/20'
                      : 'border-white/20 bg-white/5 hover:border-white/40'
                  }`}
                >
                  <div className="text-white font-medium text-sm">{voice.name}</div>
                  <div className="text-gray-400 text-xs mt-1">{voice.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Video Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Resolution/Size */}
            <div>
              <label className="block text-white font-medium mb-2">
                Resolution *
              </label>
              <select
                value={formData.size}
                onChange={(e) => setFormData({ ...formData, size: e.target.value })}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-purple-500"
              >
                <option value="1280x720">1280x720 (HD Landscape)</option>
                <option value="720x1280">720x1280 (HD Portrait)</option>
                <option value="1920x1080">1920x1080 (Full HD)</option>
                <option value="1024x1792">1024x1792 (Vertical)</option>
                <option value="1792x1024">1792x1024 (Horizontal)</option>
              </select>
            </div>

            {/* Duration */}
            <div>
              <label className="block text-white font-medium mb-2">
                Duration (seconds) *
              </label>
              <select
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) })}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-purple-500"
              >
                <option value="4">4 seconds</option>
                <option value="8">8 seconds</option>
                <option value="12">12 seconds</option>
                <option value="16">16 seconds</option>
                <option value="20">20 seconds</option>
                <option value="24">24 seconds</option>
                <option value="28">28 seconds</option>
                <option value="32">32 seconds</option>
                <option value="36">36 seconds</option>
                <option value="40">40 seconds</option>
                <option value="44">44 seconds</option>
                <option value="48">48 seconds</option>
                <option value="52">52 seconds</option>
                <option value="56">56 seconds</option>
                <option value="60">60 seconds</option>
              </select>
            </div>
          </div>

          {/* Keywords */}
          <div>
            <label className="block text-white font-medium mb-2">
              Keywords (Optional)
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addKeyword())}
                className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                placeholder="Add keyword..."
              />
              <button
                type="button"
                onClick={addKeyword}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.keywords?.map((keyword, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-purple-500/30 text-purple-200 rounded-full text-sm flex items-center gap-2"
                >
                  {keyword}
                  <button
                    type="button"
                    onClick={() => removeKeyword(index)}
                    className="hover:text-white"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Negative Keywords */}
          <div>
            <label className="block text-white font-medium mb-2">
              Negative Keywords (Optional)
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={negativeKeywordInput}
                onChange={(e) => setNegativeKeywordInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addNegativeKeyword())}
                className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                placeholder="Add negative keyword..."
              />
              <button
                type="button"
                onClick={addNegativeKeyword}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.negative_keywords?.map((keyword, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-red-500/30 text-red-200 rounded-full text-sm flex items-center gap-2"
                >
                  {keyword}
                  <button
                    type="button"
                    onClick={() => removeNegativeKeyword(index)}
                    className="hover:text-white"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Submit */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg font-medium transition-colors"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Video'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
