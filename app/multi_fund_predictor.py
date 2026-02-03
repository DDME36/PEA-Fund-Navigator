"""
Multi-Fund Predictor for PEA Provident Fund
รองรับ 4 กองทุน: PEA-F, PEA-E, PEA-G, PEA-P
พร้อม 3 โหมดความเสี่ยง: Conservative, Moderate, Aggressive
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
import yfinance as yf
from pathlib import Path
import json
from datetime import datetime

from app.config import settings


class MultiFundPredictor:
    """
    ทำนายสัดส่วนทั้ง 4 กองทุน พร้อม smoothing เพื่อลดการสวิง
    """
    
    def __init__(self, history_file: str = "models/allocation_history.json"):
        self.history_file = Path(history_file)
        self.last_allocation = self._load_last_allocation()
    
    def _load_last_allocation(self) -> Dict[str, float]:
        """โหลดสัดส่วนครั้งล่าสุด"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("last_allocation", {
                        "PEA-F": 25, "PEA-E": 25, "PEA-G": 25, "PEA-P": 25
                    })
            except:
                pass
        return {"PEA-F": 25, "PEA-E": 25, "PEA-G": 25, "PEA-P": 25}
    
    def _save_allocation(self, allocation: Dict[str, float]):
        """บันทึกสัดส่วนปัจจุบัน"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "last_allocation": allocation,
            "updated_at": datetime.now().isoformat()
        }
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def fetch_market_data(self) -> Dict[str, Any]:
        """
        ดึงข้อมูลตลาดทั้ง 4 กอง
        """
        print("Fetching market data for 4 funds...")
        
        data = {}
        
        # 1. PEA-E: Thai Equity (SET Index)
        try:
            set_data = yf.Ticker(settings.TICKER_SET).history(period="1y")
            if not set_data.empty:
                data["PEA-E"] = {
                    "return_1m": self._calculate_return(set_data, 21),
                    "return_3m": self._calculate_return(set_data, 63),
                    "return_6m": self._calculate_return(set_data, 126),
                    "volatility": self._calculate_volatility(set_data, 63),
                    "trend": self._calculate_trend(set_data),
                }
        except Exception as e:
            print(f"Warning: Failed to fetch SET data: {e}")
            data["PEA-E"] = {"return_1m": 0, "return_3m": 0, "return_6m": 0, "volatility": 15, "trend": 0}
        
        # 2. PEA-G: Global Equity (S&P 500)
        try:
            sp500_data = yf.Ticker(settings.TICKER_SP500).history(period="1y")
            if not sp500_data.empty:
                data["PEA-G"] = {
                    "return_1m": self._calculate_return(sp500_data, 21),
                    "return_3m": self._calculate_return(sp500_data, 63),
                    "return_6m": self._calculate_return(sp500_data, 126),
                    "volatility": self._calculate_volatility(sp500_data, 63),
                    "trend": self._calculate_trend(sp500_data),
                }
        except Exception as e:
            print(f"Warning: Failed to fetch S&P500 data: {e}")
            data["PEA-G"] = {"return_1m": 0, "return_3m": 0, "return_6m": 0, "volatility": 12, "trend": 0}
        
        # 3. PEA-P: REITs (average of Thai REITs)
        try:
            reits_returns = []
            for ticker in settings.TICKER_REITS:
                reit_data = yf.Ticker(ticker).history(period="1y")
                if not reit_data.empty:
                    reits_returns.append({
                        "return_1m": self._calculate_return(reit_data, 21),
                        "return_3m": self._calculate_return(reit_data, 63),
                        "return_6m": self._calculate_return(reit_data, 126),
                    })
            
            if reits_returns:
                data["PEA-P"] = {
                    "return_1m": np.mean([r["return_1m"] for r in reits_returns]),
                    "return_3m": np.mean([r["return_3m"] for r in reits_returns]),
                    "return_6m": np.mean([r["return_6m"] for r in reits_returns]),
                    "volatility": 8,  # REITs usually less volatile
                    "trend": np.mean([r["return_3m"] for r in reits_returns]) / 3,
                }
            else:
                data["PEA-P"] = {"return_1m": 0.5, "return_3m": 1.5, "return_6m": 3, "volatility": 8, "trend": 0.5}
        except Exception as e:
            print(f"Warning: Failed to fetch REITs data: {e}")
            data["PEA-P"] = {"return_1m": 0.5, "return_3m": 1.5, "return_6m": 3, "volatility": 8, "trend": 0.5}
        
        # 4. PEA-F: Fixed Income (assume stable ~2.5% annual = 0.2% monthly)
        data["PEA-F"] = {
            "return_1m": 0.2,
            "return_3m": 0.6,
            "return_6m": 1.2,
            "volatility": 1,  # Very low volatility
            "trend": 0.2,
        }
        
        return data
    
    def _calculate_return(self, df: pd.DataFrame, days: int) -> float:
        """คำนวณ return % ย้อนหลัง N วัน"""
        if len(df) < days:
            return 0
        return ((df["Close"].iloc[-1] / df["Close"].iloc[-days]) - 1) * 100
    
    def _calculate_volatility(self, df: pd.DataFrame, days: int) -> float:
        """คำนวณความผันผวน (annualized %)"""
        if len(df) < days:
            return 10
        returns = df["Close"].pct_change().dropna()
        return returns.tail(days).std() * np.sqrt(252) * 100
    
    def _calculate_trend(self, df: pd.DataFrame) -> float:
        """คำนวณแนวโน้ม (positive = ขาขึ้น, negative = ขาลง)"""
        if len(df) < 50:
            return 0
        sma_20 = df["Close"].rolling(20).mean().iloc[-1]
        sma_50 = df["Close"].rolling(50).mean().iloc[-1]
        current = df["Close"].iloc[-1]
        
        # Score: -1 to +1
        score = 0
        if current > sma_20:
            score += 0.5
        if current > sma_50:
            score += 0.3
        if sma_20 > sma_50:
            score += 0.2
        
        return score - 0.5  # Center around 0
    
    def predict_allocation(
        self, 
        risk_profile: str = "moderate",
        use_smoothing: bool = True
    ) -> Dict[str, Any]:
        """
        ทำนายสัดส่วนทั้ง 4 กอง ตามโหมดความเสี่ยง
        
        Args:
            risk_profile: "conservative", "moderate", "aggressive"
            use_smoothing: ใช้ EMA smoothing หรือไม่
        
        Returns:
            Dict with allocations and details
        """
        # Fetch market data
        market_data = self.fetch_market_data()
        
        # Get risk profile ranges
        profile = settings.RISK_PROFILES.get(risk_profile, settings.RISK_PROFILES["moderate"])
        ranges = profile["ranges"]
        
        # Calculate scores for each fund (0-100)
        scores = {}
        
        for fund, data in market_data.items():
            # Score based on return, trend, and inverse volatility
            return_score = min(100, max(0, (data["return_3m"] + 10) * 5))  # -10% to +10% → 0-100
            trend_score = min(100, max(0, (data["trend"] + 1) * 50))  # -1 to +1 → 0-100
            vol_score = min(100, max(0, 100 - data["volatility"] * 3))  # Lower vol = higher score
            
            # Weighted average
            scores[fund] = (
                return_score * 0.5 +
                trend_score * 0.3 +
                vol_score * 0.2
            )
        
        # Normalize scores within ranges
        raw_allocation = {}
        for fund in ["PEA-F", "PEA-E", "PEA-G", "PEA-P"]:
            min_pct, max_pct = ranges[fund]
            score = scores.get(fund, 50)
            
            # Map score (0-100) to range (min-max)
            raw_allocation[fund] = min_pct + (score / 100) * (max_pct - min_pct)
        
        # Normalize to 100%
        total = sum(raw_allocation.values())
        normalized = {k: (v / total) * 100 for k, v in raw_allocation.items()}
        
        # Apply smoothing (EMA)
        if use_smoothing and self.last_allocation:
            alpha = settings.ALLOCATION_SMOOTHING
            smoothed = {}
            for fund in normalized:
                old = self.last_allocation.get(fund, normalized[fund])
                new = normalized[fund]
                smoothed[fund] = alpha * old + (1 - alpha) * new
            
            # Re-normalize after smoothing
            total_smoothed = sum(smoothed.values())
            final_allocation = {k: (v / total_smoothed) * 100 for k, v in smoothed.items()}
        else:
            final_allocation = normalized
        
        # Round to integers
        final_allocation = {k: round(v) for k, v in final_allocation.items()}
        
        # Ensure sum = 100 (adjust largest)
        diff = 100 - sum(final_allocation.values())
        if diff != 0:
            largest_fund = max(final_allocation, key=final_allocation.get)
            final_allocation[largest_fund] += diff
        
        # Save for next time
        self._save_allocation(final_allocation)
        
        return {
            "allocation": final_allocation,
            "market_data": market_data,
            "scores": scores,
            "risk_profile": profile,
            "smoothing_applied": use_smoothing,
        }
    
    def get_all_risk_profiles(self) -> Dict[str, Dict]:
        """
        คำนวณสัดส่วนสำหรับทั้ง 3 โหมด
        """
        results = {}
        for profile_name in ["conservative", "moderate", "aggressive"]:
            results[profile_name] = self.predict_allocation(
                risk_profile=profile_name,
                use_smoothing=True
            )
        return results
