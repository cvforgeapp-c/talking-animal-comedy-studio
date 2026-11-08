// app/page.tsx
'use client';

import { useState } from 'react';

export default function Home() {
  const [characterPrompt, setCharacterPrompt] = useState('');
  const [motionPrompt, setMotionPrompt] = useState('');
  const [dialogue, setDialogue] = useState('');
  const [referenceFile, setReferenceFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus('processing');

    const formData = new FormData();
    formData.append('motion_prompt', motionPrompt);
    formData.append('character_description', characterPrompt);
    formData.append('dialogue_script', dialogue);
    if (referenceFile) {
      formData.append('reference_image', referenceFile);
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/generate-video', {
        method: 'POST',
        body: formData,
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
    }, 4000);
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-6">
      <div className="max-w-xl w-full bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl">
        <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 mb-2">
          Talking Animal & Comedy Studio
        </h1>
        <p className="text-slate-400 mb-6 text-sm">
          Generate or animate consistent 3D cinematic characters locally with voice lines.
        </p>

        <form onSubmit={handleGenerate} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Upload Character Reference Image (Optional - locks identity)
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setReferenceFile(e.target.files?.[0] || null)}
              className="w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-purple-600 file:text-white hover:file:bg-purple-500 cursor-pointer"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Character Prompt (If no image uploaded)
            </label>
            <textarea
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white text-sm outline-none resize-none h-20"
              placeholder="e.g., A giant angry onion character..."
              value={characterPrompt}
              onChange={(e) => setCharacterPrompt(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Motion / Action Prompt
            </label>
            <textarea
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white text-sm outline-none resize-none h-20"
              placeholder="e.g., Turns aggressively and gestures toward the camera..."
              value={motionPrompt}
              onChange={(e) => setMotionPrompt(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Character Dialogue / Comedy Line (Spoken Audio)
            </label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white text-sm outline-none"
              placeholder="e.g., 'Why did the developer cross the road? To debug the other side!'"
              value={dialogue}
              onChange={(e) => setDialogue(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 rounded-lg font-bold transition-all ${
              loading
                ? 'bg-purple-800 cursor-not-allowed opacity-50'
                : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-90 shadow-lg'
            }`}
          >
            {loading ? `Generating Video (${status})...` : 'Generate Cinematic Video 🎬'}
          </button>
        </form>

        {jobId && (
          <div className="mt-6 p-4 bg-slate-950 border border-slate-800 rounded-xl text-center">
            <p className="text-sm text-slate-400 mb-2">
              Job ID: <span className="text-purple-400">{jobId}</span>
            </p>
            <p className="text-sm font-semibold capitalize mb-4">
              Status:{' '}
              <span className={status === 'completed' ? 'text-green-400' : status === 'failed' ? 'text-red-400' : 'text-yellow-400 animate-pulse'}>
                {status}
              </span>
            </p>

            {status === 'completed' && (
              <div className="space-y-4">
                <video controls className="w-full rounded-lg border border-slate-800" src={`http://localhost:8000/api/v1/download/${jobId}`} />
                <a href={`http://localhost:8000/api/v1/download/${jobId}`} download className="inline-block bg-green-600 hover:bg-green-500 text-white font-bold py-2 px-6 rounded-lg text-sm">
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
