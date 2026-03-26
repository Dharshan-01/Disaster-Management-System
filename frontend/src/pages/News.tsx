import { useEffect, useState, useCallback } from 'react';
import { Newspaper, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { NewsItem } from '../types';
import NewsCard from '../components/NewsCard';

const ALL_TYPES = ['all', 'wildfire', 'flood', 'cyclone', 'earthquake', 'landslide'];

export default function News() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState('all');

  const fetchNews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getNews();
      setNews(Array.isArray(data) ? (data as NewsItem[]) : []);
    } catch {
      setError('Unable to load news. Please try refreshing.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  async function handleRefresh() {
    setRefreshing(true);
    try {
      await api.refreshNews();
      await fetchNews();
    } catch {
      setError('Refresh failed. Please try again.');
    } finally {
      setRefreshing(false);
    }
  }

  const filtered =
    filter === 'all'
      ? news
      : news.filter(item =>
          item.disaster_tags.some(tag => tag.toLowerCase() === filter)
        );

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Newspaper className="text-blue-400" size={24} />
            <div>
              <h1 className="text-2xl font-bold">Public News Feed</h1>
              <p className="text-gray-400 text-sm">Latest disaster-related news and updates</p>
            </div>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing || loading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-900/40 border border-red-600/50 rounded-lg px-4 py-3 text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Filter Tabs */}
        <div className="flex flex-wrap gap-2">
          {ALL_TYPES.map(type => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium capitalize transition-colors ${
                filter === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 border border-gray-600 hover:bg-gray-700'
              }`}
            >
              {type === 'all' ? 'All' : type}
              {type !== 'all' && (
                <span className="ml-1.5 text-xs text-gray-400">
                  ({news.filter(n => n.disaster_tags.some(t => t.toLowerCase() === type)).length})
                </span>
              )}
            </button>
          ))}
          {filter !== 'all' && (
            <span className="self-center text-gray-500 text-sm ml-2">
              {filtered.length} article{filtered.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>

        {/* News Grid */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-56 bg-gray-800 border border-gray-700 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-12 text-center text-gray-500">
            {news.length === 0
              ? 'No news articles available. Click Refresh to fetch the latest news.'
              : `No articles found for "${filter}".`}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map(item => (
              <NewsCard key={item.id} news={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
