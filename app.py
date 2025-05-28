// Interface Web - Dual Momentum App avec React + Tailwind + Recharts
// Affiche la performance sur 6M/12M de 5 actifs (SXR8, ACWX, AGG, TLT, IRX)
// Donne une recommandation automatique selon la stratégie Dual Momentum

import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from "recharts";

const tickers = ["SXR8.DE", "ACWX", "AGG", "TLT", "%5EIRX"];
const tickerNames = {
  "SXR8.DE": "Actions US (SXR8)",
  "ACWX": "Actions Monde (ACWX)",
  "AGG": "Obligations CT (AGG)",
  "TLT": "Obligations LT (TLT)",
  "%5EIRX": "T-Bills (US03MY)"
};

export default function DualMomentumApp() {
  const [results, setResults] = useState([]);
  const [recommendation, setRecommendation] = useState(null);

  useEffect(() => {
    async function fetchData() {
      const now = new Date();
      const date6m = new Date(now);
      date6m.setMonth(now.getMonth() - 6);
      const date12m = new Date(now);
      date12m.setFullYear(now.getFullYear() - 1);

      const fetchTicker = async (ticker) => {
        const res = await fetch(
          `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?range=1y&interval=1d`
        );
        const data = await res.json();
        const close = data.chart.result[0].indicators.quote[0].close;
        const timestamps = data.chart.result[0].timestamp.map((ts) => new Date(ts * 1000));

        const priceToday = close[close.length - 1];
        const price6m = close[timestamps.findIndex((t) => t >= date6m)];
        const price12m = close[0];

        return {
          ticker,
          name: tickerNames[ticker],
          perf6m: ((priceToday - price6m) / price6m) * 100,
          perf12m: ((priceToday - price12m) / price12m) * 100
        };
      };

      const all = await Promise.all(tickers.map(fetchTicker));
      setResults(all);

      // Analyse Dual Momentum
      const actions = Math.max(
        all.find((x) => x.ticker === "SXR8.DE")?.perf12m || -999,
        all.find((x) => x.ticker === "ACWX")?.perf12m || -999
      );
      const oblig = Math.max(
        all.find((x) => x.ticker === "AGG")?.perf12m || -999,
        all.find((x) => x.ticker === "TLT")?.perf12m || -999
      );
      const tbills = all.find((x) => x.ticker === "%5EIRX")?.perf12m || 0;

      let reco = "";
      if (actions > oblig) {
        reco = actions > tbills ? "Investir en actions" : "Rester en cash (T-Bills > Actions)";
      } else {
        reco = oblig > tbills ? "Investir en obligations" : "Rester en cash (T-Bills > Obligations)";
      }
      setRecommendation(reco);
    }

    fetchData();
  }, []);

  return (
    <div className="p-4 grid gap-4">
      <h1 className="text-2xl font-bold">Dual Momentum Tracker</h1>
      {results.map((asset) => (
        <Card key={asset.ticker} className="shadow-md">
          <CardContent className="p-4">
            <div className="text-lg font-semibold">{asset.name}</div>
            <div>6M : {asset.perf6m.toFixed(2)} %</div>
            <div>12M : {asset.perf12m.toFixed(2)} %</div>
          </CardContent>
        </Card>
      ))}

      {recommendation && (
        <div className="p-4 bg-green-100 rounded-xl text-lg font-bold">
          📈 Recommandation : {recommendation}
        </div>
      )}
    </div>
  );
}
