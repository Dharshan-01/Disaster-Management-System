import { ExternalLink } from 'lucide-react';
import { NewsItem } from '../types';

interface NewsCardProps {
  news: NewsItem;
}

const TAG_COLORS: Record<string, string> = {
  wildfire:   'bg-orange-500/20 text-orange-300 border-orange-500/40',
  flood:      'bg-blue-500/20 text-blue-300 border-blue-500/40',
  cyclone:    'bg-purple-500/20 text-purple-300 border-purple-500/40',
  earthquake: 'bg-red-500/20 text-red-300 border-red-500/40',
  landslide:  'bg-yellow-500/20 text-yellow-300 border-yellow-500/40',
};

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: 'numeric', month: 'short', day: 'numeric'
    });
  } catch {
    return iso;
  }
}

export default function NewsCard({ news }: NewsCardProps) {
  return (
    <article className="bg-gray-800 border border-gray-700 rounded-xl p-4 flex flex-col gap-3 hover:border-gray-500 transition-colors">
      <div className="flex flex-wrap gap-1.5">
        {news.disaster_tags.map(tag => (
          <span
            key={tag}
            className={`text-xs font-medium px-2 py-0.5 rounded-full border capitalize ${
              TAG_COLORS[tag.toLowerCase()] ?? 'bg-gray-600/40 text-gray-300 border-gray-500/40'
            }`}
          >
            {tag}
          </span>
        ))}
      </div>

      <h3 className="text-white font-semibold text-sm leading-snug line-clamp-2">{news.title}</h3>
      <p className="text-gray-400 text-xs leading-relaxed line-clamp-3">{news.summary}</p>

      <div className="flex items-center justify-between mt-auto pt-2 border-t border-gray-700">
        <div className="flex flex-col">
          <span className="text-gray-400 text-xs font-medium">{news.source}</span>
          <span className="text-gray-500 text-xs">{formatDate(news.published_at)}</span>
        </div>
        {news.link && (
          <a
            href={news.link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-blue-400 hover:text-blue-300 text-xs font-medium transition-colors"
          >
            Read more <ExternalLink size={12} />
          </a>
        )}
      </div>
    </article>
  );
}
