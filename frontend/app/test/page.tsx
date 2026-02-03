"use client";

import { useEffect, useState } from "react";

export default function TestPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/data/prediction.json")
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;
  if (!data) return <div className="p-8">No data</div>;

  return (
    <div className="min-h-screen p-8 bg-zinc-950 text-white">
      <h1 className="text-2xl font-bold mb-4">🧪 Test Page - Data Check</h1>
      
      <div className="space-y-4">
        <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
          <h2 className="font-bold mb-2">✅ Basic Info</h2>
          <p>Updated: {data.updated_at}</p>
          <p>Prediction: {data.prediction?.prediction}</p>
          <p>Confidence: {(data.prediction?.probability * 100).toFixed(1)}%</p>
        </div>

        <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
          <h2 className="font-bold mb-2">🛡️ Risk Management</h2>
          {data.prediction?.risk_management ? (
            <div>
              <p className="text-green-400">✓ HAS risk_management</p>
              <p>Allocation: {data.prediction.risk_management.allocation}%</p>
              <p>Reason: {data.prediction.risk_management.reason}</p>
            </div>
          ) : (
            <p className="text-red-400">✗ NO risk_management</p>
          )}
        </div>

        <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
          <h2 className="font-bold mb-2">📊 Multi-Fund (4 กอง)</h2>
          {data.prediction?.multi_fund ? (
            <div>
              <p className="text-green-400">✓ HAS multi_fund</p>
              <div className="mt-2 space-y-1 text-sm">
                <p>Conservative: {JSON.stringify(data.prediction.multi_fund.conservative)}</p>
                <p>Moderate: {JSON.stringify(data.prediction.multi_fund.moderate)}</p>
                <p>Aggressive: {JSON.stringify(data.prediction.multi_fund.aggressive)}</p>
              </div>
            </div>
          ) : (
            <p className="text-red-400">✗ NO multi_fund</p>
          )}
        </div>

        <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
          <h2 className="font-bold mb-2">📈 Market Data (4 กอง)</h2>
          {data.prediction?.multi_fund?.market_data ? (
            <div className="space-y-1 text-sm">
              {Object.entries(data.prediction.multi_fund.market_data).map(([fund, info]: [string, any]) => (
                <p key={fund}>
                  {fund}: {info.return_3m?.toFixed(2)}% (3m)
                </p>
              ))}
            </div>
          ) : (
            <p className="text-red-400">✗ NO market_data</p>
          )}
        </div>

        <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
          <h2 className="font-bold mb-2">🔧 Model Info</h2>
          <p>Type: {data.model_info?.type}</p>
          <p>Ticker: {data.model_info?.ticker}</p>
        </div>
      </div>

      <div className="mt-8">
        <a href="/" className="px-4 py-2 bg-cyan-500 text-white rounded hover:bg-cyan-600">
          ← กลับหน้าหลัก
        </a>
      </div>
    </div>
  );
}
