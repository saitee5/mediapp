import { LiveTranscriber } from './components/LiveTranscriber';

export function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-cyan-500 selection:text-black">
      <main className="flex-1 py-8 sm:py-12">
        <LiveTranscriber />
      </main>

      <footer className="py-6 text-center text-xs text-slate-600 border-t border-slate-900 font-mono">
        Built with React, Vite, Tailwind CSS, FastAPI, and Groq Cloud LPU
      </footer>
    </div>
  );
}

export default App;
