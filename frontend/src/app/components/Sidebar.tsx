import { useState } from 'react';
import { useRepolensApi } from '../utils/api';
import { useGraphData } from '../context/GraphDataProvider';

export default function Sidebar() {
  const { graph } = useGraphData();
  const { askRepoQuestion } = useRepolensApi();
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<{ q: string; a: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    if (!graph || !graph.nodes || !graph.edges) {
      setError('Please analyze a repository first before asking questions.');
      return;
    }

    // Check if graph is very large
    const nodeCount = graph.nodes?.length || 0;
    const edgeCount = graph.edges?.length || 0;

    if (nodeCount > 1000 || edgeCount > 2000) {
      setError(
        'Graph is very large. The AI will use a simplified analysis to avoid token limits.',
      );
    }

    setLoading(true);
    setError(null);
    try {
      const data = await askRepoQuestion(graph, question);
      setHistory(
        [
          { q: question, a: data.answer || 'No answer from AI.' },
          ...history,
        ].slice(0, 5),
      );
    } catch (err) {
      setError('Failed to get answer from AI.');
    } finally {
      setLoading(false);
      setQuestion('');
    }
  };

  return (
    <aside className='bg-sidebar flex h-full w-80 min-w-[18rem] flex-col border-r border-white/10 p-4 shadow-xl transition-all duration-300'>
      {/* Mobile close button */}
      <button
        className='bg-primary/90 absolute top-4 right-4 z-10 rounded-lg p-1 text-white md:hidden'
        onClick={() => {
          // This will be handled by the parent component
          const event = new CustomEvent('closeSidebar');
          window.dispatchEvent(event);
        }}
      >
        <svg
          className='h-4 w-4'
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M6 18L18 6M6 6l12 12'
          />
        </svg>
      </button>

      <h2 className='text-primary mb-2 text-lg font-bold'>Ask RepoLens AI</h2>
      <p className='mb-3 text-xs text-gray-400'>
        Ask about classes, functions, code structure, and implementation details
      </p>
      <form onSubmit={handleAsk} className='mb-4 flex flex-col gap-2'>
        <textarea
          className='bg-background focus:ring-primary h-20 resize-none rounded-sm border border-white/10 p-2 text-black focus:ring-2 focus:outline-hidden'
          placeholder={
            !graph || !graph.nodes
              ? 'Please analyze a repository first...'
              : 'Ask about the codebase...'
          }
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading || !graph || !graph.nodes}
        />
        <button
          type='submit'
          className='bg-primary hover:bg-primary/80 rounded-sm px-4 py-2 font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50'
          disabled={loading || !graph || !graph.nodes}
        >
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </form>
      {error && <div className='mb-2 text-red-400'>{error}</div>}
      <div className='flex-1 overflow-auto'>
        <h3 className='mb-1 font-semibold text-white'>Recent Questions</h3>
        <ul className='space-y-2'>
          {history.map((item, i) => (
            <li
              key={i}
              className='bg-background/80 rounded-sm border border-white/5 p-2 text-sm shadow-sm'
            >
              <div className='text-primary font-medium'>Q: {item.q}</div>
              <div className='text-white/80'>A: {item.a}</div>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
