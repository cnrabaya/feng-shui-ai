import "./styles.css";

export default function App() {
  return (
    <div className="min-h-screen bg-stone-50 flex flex-col items-center justify-center p-8">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-stone-800">FengShuiAI</h1>
        <p className="text-stone-500 mt-2">Upload your room. Unlock its energy.</p>
      </header>

      <main className="w-full max-w-2xl">
        <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-8 text-center">
          <p className="text-stone-400">Photo upload coming soon…</p>
        </div>
      </main>
    </div>
  );
}