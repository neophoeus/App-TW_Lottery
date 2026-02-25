'use client';
import { useState, useEffect, useCallback } from 'react';
import { GameSelector } from '@/components/GameSelector';
import { PredictionCard } from '@/components/PredictionCard';
import { Sparkles, RefreshCw, BarChart3, DownloadCloud, Trophy, Info } from 'lucide-react';

interface StrategyResult {
  name: string;
  desc: string;
  nums: number[];
  special: number;
}

interface PredictionResponse {
  game: string;
  last_date: string;
  total_draws: number;
  strategies: StrategyResult[];
}

export default function Home() {
  const [selectedGame, setSelectedGame] = useState('power');
  const [data, setData] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  const fetchPrediction = useCallback(async (retryCount = 0) => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/predict/${selectedGame}`);
      if (!res.ok) throw new Error('Failed to fetch');
      const json = await res.json();
      await new Promise(r => setTimeout(r, 600));
      setData(json);
    } catch (error) {
      console.warn(`Fetch prediction failed (attempt ${retryCount + 1}):`, error);
      if (retryCount < 10) { // Retry up to 10 times for backend startup
        await new Promise(r => setTimeout(r, 2000));
        fetchPrediction(retryCount + 1);
        return;
      }
      console.error('All retries failed:', error);
    } finally {
      if (retryCount === 0 || data) { // Only stop loading if we got data or exhausted initial flow (recursive calls manage their own loading state)
        setLoading(false);
      }
    }
  }, [selectedGame, data]);

  const updateData = async () => {
    setUpdating(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/update`, { method: 'POST' });
      const json = await res.json();
      if (json.status === 'success') {
        alert(`資料更新成功！\n${JSON.stringify(json.details, null, 2)}`);
        fetchPrediction();
      } else {
        alert('更新失敗');
      }
    } catch (e) {
      console.error(e);
      alert('無法連接伺服器');
    } finally {
      setUpdating(false);
    }
  };

  useEffect(() => {
    fetchPrediction(0);
  }, [selectedGame]); // Only re-fetch on game change, not on fetchPrediction reference change which causes loops with retry logic

  // Separate Ensemble
  const ensembleStrategy = data?.strategies.find(s => s.name === '綜合預測');
  const otherStrategies = data?.strategies.filter(s => s.name !== '綜合預測') || [];

  return (
    <main className="min-h-screen py-12 px-4 selection:bg-amber-400 selection:text-red-900">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <header className="text-center mb-12">
          <div className="inline-block bg-red-900 text-amber-400 px-6 py-2 rounded-full font-bold mb-6 border-2 border-amber-500 shadow-lg glow">
            ✨ AI 智能運算 • 精準預測 ✨
          </div>

          <h1 className="text-5xl md:text-6xl font-black mb-8 text-amber-300 drop-shadow-[0_4px_4px_rgba(0,0,0,0.8)] tracking-wide">
            台灣彩券 AI 預測
          </h1>
        </header>

        {/* Controls */}
        <section className="flex flex-col items-center gap-8 mb-16">
          <GameSelector selectedPath={selectedGame} onSelect={setSelectedGame} />

          <div className="flex gap-6">
            <button
              onClick={() => fetchPrediction(0)}
              disabled={loading || updating}
              className="bg-amber-500 hover:bg-amber-400 text-red-900 px-10 py-4 rounded-full font-black text-xl shadow-[0_4px_0_#b45309] active:shadow-none active:translate-y-1 transition-all flex items-center gap-3 border-2 border-amber-300"
            >
              <RefreshCw className={`w-6 h-6 ${loading ? 'animate-spin' : ''}`} />
              {loading && !data ? '喚醒 AI 引擎中...' : loading ? '運算中...' : '重新預測'}
            </button>

            <button
              onClick={updateData}
              disabled={updating || loading}
              className="bg-red-800 hover:bg-red-700 text-amber-100 px-8 py-4 rounded-full font-bold text-lg shadow-[0_4px_0_#450a0a] active:shadow-none active:translate-y-1 transition-all flex items-center gap-3 border-2 border-red-600"
            >
              <DownloadCloud className={`w-5 h-5 ${updating ? 'animate-bounce' : ''}`} />
              {updating ? '更新中...' : '更新資料'}
            </button>
          </div>
        </section>

        {/* Latest Info */}
        {data && (
          <div className="mb-12 text-center">
            <div className="inline-block bg-red-950/80 px-8 py-3 rounded-xl border border-red-800 text-amber-200 font-bold shadow-lg">
              <BarChart3 className="w-5 h-5 inline-block mr-2 -mt-1" />
              最新開獎: {data.last_date} | 樣本數: {data.total_draws} 期
            </div>
          </div>
        )}

        {/* HERO: Ensemble Strategy */}
        {(loading || ensembleStrategy) && (
          <div className="mb-16">
            <div className="bg-gradient-to-br from-yellow-300 via-amber-400 to-yellow-500 rounded-[3rem] p-1 shadow-[0_20px_50px_rgba(245,158,11,0.3)] border-4 border-amber-200 transform hover:scale-[1.01] transition-transform duration-300">
              <div className="bg-amber-400/20 backdrop-blur-sm rounded-[2.8rem] p-8 md:p-12 text-center md:text-left">
                <div className="flex flex-col xl:flex-row items-center justify-between gap-10">
                  <div className="max-w-xl">
                    <div className="inline-block bg-red-600 text-white px-4 py-1 rounded-full text-xs font-black uppercase tracking-wider mb-4 shadow-md">
                      <Trophy className="w-3 h-3 inline mr-1" />
                      冠軍推薦 Top Pick
                    </div>
                    <h2 className="text-4xl md:text-5xl font-black text-red-900 mb-4 drop-shadow-sm">
                      {loading && !data ? '連接 AI 引擎...' : loading ? '計算綜合結果...' : ensembleStrategy?.name}
                    </h2>
                    <p className="text-red-900/80 text-xl font-bold mb-6 leading-relaxed">
                      {loading ? '正在統計所有模型票數...' : ensembleStrategy?.desc}
                    </p>

                    <div className="bg-white/40 rounded-xl p-4 border border-white/50 text-red-900 text-sm font-semibold flex gap-3 text-left shadow-sm flex-col">
                      <div className="flex gap-3">
                        <Info className="w-5 h-5 shrink-0 mt-0.5" />
                        <span>綜合熱門、平衡、馬可夫鏈、LSTM 等所有策略模型的投票結果，選出共識最高的「黃金組合」，穩定性最高。</span>
                      </div>
                      {ensembleStrategy?.desc.includes('細節:') && (
                        <div className="mt-2 pt-2 border-t border-red-900/10 text-xs font-mono tracking-tight text-red-800 break-words opacity-80">
                          {ensembleStrategy?.desc.split('細節:')[1]}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Hero Balls */}
                  <div className="flex flex-wrap justify-center gap-4">
                    {loading ? (
                      Array.from({ length: 7 }).map((_, i) => (
                        <div key={i} className="w-20 h-20 rounded-full bg-white/30 animate-pulse border-4 border-white/50" />
                      ))
                    ) : (
                      <>
                        {ensembleStrategy?.nums.map((num, idx) => (
                          <div key={idx} className="w-20 h-20 md:w-24 md:h-24 rounded-full bg-red-700 shadow-[0_8px_16px_rgba(0,0,0,0.3)] flex items-center justify-center font-black text-white text-4xl border-4 border-red-500 ring-4 ring-amber-300/50">
                            {num}
                          </div>
                        ))}
                        {ensembleStrategy?.special > 0 && (
                          <div className="w-20 h-20 md:w-24 md:h-24 rounded-full bg-amber-500 shadow-[0_8px_16px_rgba(0,0,0,0.3)] flex items-center justify-center font-black text-red-900 text-4xl border-4 border-amber-300 ring-4 ring-red-500/50 ml-2">
                            {ensembleStrategy.special}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Grid Area - 2 Columns on Desktop */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-2 gap-8">
          {loading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <PredictionCard
                key={i}
                name="運算中..."
                desc="Please wait..."
                numbers={[]}
                special={0}
                loading={true}
              />
            ))
          ) : otherStrategies.map((strategy, idx) => (
            <PredictionCard
              key={idx}
              name={strategy.name}
              desc={strategy.desc}
              numbers={strategy.nums}
              special={strategy.special}
            />
          ))}
        </div>

        {/* Footer */}
        <footer className="mt-24 text-center border-t-2 border-red-900 pt-8 pb-8">
          <p className="text-amber-500/60 font-medium">
            © 2026 TW Lottery AI | 祝您中大獎 ! Good Luck !
          </p>
        </footer>
      </div>
    </main>
  );
}
