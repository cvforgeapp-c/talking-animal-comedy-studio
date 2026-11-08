// app/page.tsx
'use client';

import { useState } from 'react';

export default function Home() {
  const [characterPrompt, setCharacterPrompt] = useState('');
  const [motionPrompt, setMotionPrompt] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');
  const [loading, setLoading] = useState(false);

  // 1. Submit Generation Request to FastAPI Backend
  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus('processing');

    try {
      const response = await fetch('http://localhost:8000/api/v1/generate-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_description: characterPrompt,
          motion_prompt: motionPrompt,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setJobId(data.job_id);
        pollJobStatus(data.job_id);
      } else {
        alert('Failed to start job');
        setLoading(false);
      }
    } catch (err) {
      console.error(err);
      alert('Error connecting to backend server.');
      setLoading(false);
    }
  };

  // 2. Poll Backend for Job Completion Status
  const pollJobStatus = (id: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/status/${id}`);
        const data = await res.json();

        setStatus(data.status);

        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(interval);
          setLoading(false);
        }
      } catch (err) {
        console.error('Polling error:', err);
        clearInterval(interval);
        setLoading(false);
      }
    }, 4000); // Check every 4 seconds
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-6">
      <div className="max-w-xl w-full bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl">
        
        <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 mb-2">
          Talking Animal & Comedy Studio
        </h1>
        <p className="text-slate-400 mb-6 text-sm">
          Generate cinematic 3D character keyframes and animated video clips locally.
        </p>

        <form onSubmit={handleGenerate} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Character Description (Pixar / 3D Style)
            </label>
            <textarea
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none resize-none h-24 text-sm"
              placeholder="e.g., A cute crying tomato wearing a traditional Indian saree..."
              value={characterPrompt}
              onChange={(e) => setCharacterPrompt(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Motion Prompt (Animation / Expression)
            </label>
            <textarea
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none resize-none h-24 text-sm"
              placeholder="e.g., Sobbing emotionally, shoulders shaking, tears rolling down cheeks..."
              value={motionPrompt}
              onChange={(e) => setMotionPrompt(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 rounded-lg font-bold transition-all ${
              loading
                ? 'bg-purple-800 cursor-not-allowed opacity-50'
                : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-90 shadow-lg shadow-purple-900/30'
            }`}
          >
            {loading ? `Generating Video (${status})...` : 'Generate 3D Video 🎬'}
          </button>
        </form>

        {/* Status / Output Section */}
        {jobId && (
          <div className="mt-6 p-4 bg-slate-950 border border-slate-800 rounded-xl text-center">
            <p className="text-sm text-slate-400 mb-2">
              Job ID: <span className="text-mono text-purple-400">{jobId}</span>
            </p>
            <p className="text-sm font-semibold capitalize mb-4">
              Current Status:{' '}
              <span
                className={
                  status === 'completed'
                    ? 'text-green-400'
                    : status === 'failed'
                    ? 'text-red-400'
                    : 'text-yellow-400 animate-pulse'
                }
              >
                {status}
              </span>
            </p>

            {status === 'completed' && (
              <div className="space-y-4">
                <video
                  controls
                  className="w-full rounded-lg border border-slate-800"
                  src={`http://localhost:8000/api/v1/download/${jobId}`}
                />
                <a
                  href={`http://localhost:8000/api/v1/download/${jobId}`}
                  download
                  className="inline-block bg-green-600 hover:bg-green-500 text-white font-bold py-2 px-6 rounded-lg text-sm transition-all"
                >
                  Download MP4 📥
                </a>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
