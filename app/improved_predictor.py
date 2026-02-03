"""
Improved Predictor - แก้ปัญหา Bearish Bias และเพิ่มความแม่นยำ
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from app.monthly_ml import MonthlyMLPredictor


class ImprovedPredictor(MonthlyMLPredictor):
    """
    ปรับปรุงโมเดลเดิมด้วย:
    1. Trend-Aware Adjustment - ถ้า trend แข็งแกร่ง ให้น้ำหนัก Bullish มากขึ้น
    2. Momentum Boost - ใช้ momentum ช่วยตัดสิน
    3. Confidence Calibration - ปรับ confidence ให้สมเหตุสมผล
    4. Anti-Bearish Bias - ลด bias ที่ทายลงบ่อยเกินไป
    """
    
    def predict_with_trend_adjustment(
        self, 
        monthly: pd.DataFrame
    ) -> Tuple[int, float, Dict]:
        """
        ทำนายพร้อมปรับตาม trend
        """
        # Get base prediction from ML
        base_prediction, base_confidence, ml_details = self.predict(monthly)
        
        # Get trend analysis
        trend_data = self.get_trend_analysis(monthly)
        
        # Calculate adjustment factors
        trend_score = trend_data.get("trend_score", 50) / 100  # 0-1
        momentum_3m = trend_data.get("momentum", {}).get("3m", 0)
        momentum_6m = trend_data.get("momentum", {}).get("6m", 0)
        
        # Get current features
        df = self.create_features(monthly)
        df_clean = df.dropna(subset=self.feature_columns)
        latest = df_clean.iloc[-1]
        
        drawdown = latest.get("Drawdown", 0)
        rsi_6 = latest.get("RSI_6", 50)
        
        # Adjustment logic
        bullish_signals = 0
        bearish_signals = 0
        
        # 1. Trend signals
        if trend_score > 0.7:  # Strong uptrend
            bullish_signals += 2
        elif trend_score > 0.5:  # Mild uptrend
            bullish_signals += 1
        elif trend_score < 0.3:  # Strong downtrend
            bearish_signals += 2
        elif trend_score < 0.5:  # Mild downtrend
            bearish_signals += 1
        
        # 2. Momentum signals
        if momentum_3m > 3 and momentum_6m > 5:  # Strong momentum
            bullish_signals += 2
        elif momentum_3m > 0 and momentum_6m > 0:  # Positive momentum
            bullish_signals += 1
        elif momentum_3m < -3 and momentum_6m < -5:  # Negative momentum
            bearish_signals += 2
        elif momentum_3m < 0 and momentum_6m < 0:
            bearish_signals += 1
        
        # 3. RSI signals (contrarian)
        if rsi_6 < 30:  # Oversold → likely to bounce
            bullish_signals += 1
        elif rsi_6 > 70:  # Overbought → likely to correct
            bearish_signals += 1
        
        # 4. Drawdown signals
        if drawdown < -15:  # Deep drawdown → oversold
            bullish_signals += 1
        elif drawdown > -5:  # Near peak → be careful
            bearish_signals += 1
        
        # Calculate total signal strength
        total_signals = bullish_signals + bearish_signals
        if total_signals > 0:
            bullish_ratio = bullish_signals / total_signals
        else:
            bullish_ratio = 0.5
        
        # Combine ML prediction with signals
        ml_bullish_prob = ml_details["ensemble_proba"]["up"]
        ml_bearish_prob = ml_details["ensemble_proba"]["down"]
        
        # Weighted average (60% ML, 40% signals)
        adjusted_bullish_prob = 0.6 * ml_bullish_prob + 0.4 * bullish_ratio
        adjusted_bearish_prob = 1 - adjusted_bullish_prob
        
        # Final prediction
        if adjusted_bullish_prob > 0.5:
            final_prediction = 1
            final_confidence = adjusted_bullish_prob
        else:
            final_prediction = 0
            final_confidence = adjusted_bearish_prob
        
        # Add adjustment details
        ml_details["adjustment"] = {
            "base_prediction": "Bullish" if base_prediction == 1 else "Bearish",
            "base_confidence": base_confidence,
            "trend_score": trend_score,
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals,
            "signal_ratio": bullish_ratio,
            "adjusted_prediction": "Bullish" if final_prediction == 1 else "Bearish",
            "adjusted_confidence": final_confidence,
            "changed": final_prediction != base_prediction
        }
        
        return final_prediction, final_confidence, ml_details
    
    def get_recommendation_text(
        self,
        prediction: int,
        confidence: float,
        trend_data: Dict
    ) -> str:
        """
        สร้างคำแนะนำที่สมเหตุสมผล
        """
        trend_score = trend_data.get("trend_score", 50)
        momentum_3m = trend_data.get("momentum", {}).get("3m", 0)
        
        if prediction == 1:  # Bullish
            if confidence > 0.7 and trend_score > 70:
                return "📈 สัญญาณดีมาก! แนวโน้มขาขึ้นแข็งแกร่ง เหมาะลงทุนหุ้น"
            elif confidence > 0.6:
                return "⛅ สัญญาณค่อนข้างดี แนวโน้มขาขึ้น เพิ่มสัดส่วนหุ้นได้"
            else:
                return "🌤️ สัญญาณบวกอ่อนๆ ระมัดระวังแต่ยังถือหุ้นได้"
        else:  # Bearish
            if confidence > 0.7 and trend_score < 30:
                return "🌧️ สัญญาณไม่ดี! แนวโน้มขาลง ควรลดสัดส่วนหุ้น"
            elif confidence > 0.6:
                return "🌦️ สัญญาณค่อนข้างลบ ระมัดระวัง ลดหุ้นเพิ่มตราสารหนี้"
            else:
                return "🌥️ สัญญาณกลางๆ ไม่แน่ใจ รักษาสมดุล"
    
    def backtest_improved(self, monthly: pd.DataFrame, initial_capital: float = 100000) -> Dict[str, Any]:
        """
        Backtest with improved prediction
        """
        df = self.create_features(monthly)
        df_clean = df.dropna(subset=self.feature_columns + ["Target"])
        
        if len(df_clean) < 30:
            raise ValueError("Not enough data for backtest")
        
        results = []
        capital = initial_capital
        
        start_idx = int(len(df_clean) * 0.7)
        
        for i in range(start_idx, len(df_clean) - 1):
            # Simulate prediction at this point
            historical_data = df_clean.iloc[:i+1].copy()
            monthly_subset = monthly.iloc[:i+1].copy()
            
            # Get improved prediction
            try:
                prediction, confidence, _ = self.predict_with_trend_adjustment(monthly_subset)
            except:
                # Fallback to base prediction
                X = df_clean[self.feature_columns].iloc[i:i+1]
                X_scaled = self.scaler.transform(X)
                prediction = self.model.predict(X_scaled)[0]
                proba = self.model.predict_proba(X_scaled)[0]
                confidence = float(proba[prediction])
            
            current = df_clean.iloc[i]
            next_row = df_clean.iloc[i + 1]
            
            # Calculate allocation
            if prediction == 1:
                if confidence >= 0.7:
                    allocation = 1.0
                elif confidence >= 0.6:
                    allocation = 0.7
                else:
                    allocation = 0.5
            else:
                if confidence >= 0.7:
                    allocation = 0.0
                elif confidence >= 0.6:
                    allocation = 0.3
                else:
                    allocation = 0.5
            
            # Calculate returns
            actual_return = (next_row["Close"] - current["Close"]) / current["Close"]
            actual_direction = 1 if actual_return > 0 else 0
            
            bond_return = 0.003
            portfolio_return = actual_return * allocation + bond_return * (1 - allocation)
            
            capital *= (1 + portfolio_return)
            
            results.append({
                "date": current.name if hasattr(current, 'name') else i,
                "prediction": int(prediction),
                "actual": actual_direction,
                "confidence": confidence,
                "allocation": allocation,
                "actual_return": actual_return,
                "portfolio_return": portfolio_return,
                "capital": capital,
                "correct": prediction == actual_direction
            })
        
        # Calculate metrics (same as before)
        results_df = pd.DataFrame(results)
        
        total_trades = len(results_df)
        correct_trades = results_df["correct"].sum()
        win_rate = correct_trades / total_trades if total_trades > 0 else 0
        
        total_return = (capital - initial_capital) / initial_capital * 100
        buy_hold_return = (df_clean["Close"].iloc[-1] - df_clean["Close"].iloc[start_idx]) / df_clean["Close"].iloc[start_idx] * 100
        
        monthly_returns = results_df["portfolio_return"]
        if len(monthly_returns) > 1 and monthly_returns.std() > 0:
            sharpe = (monthly_returns.mean() * 12) / (monthly_returns.std() * np.sqrt(12))
        else:
            sharpe = 0
        
        cumulative = (1 + results_df["portfolio_return"]).cumprod()
        peak = cumulative.expanding().max()
        drawdown = (cumulative - peak) / peak
        max_drawdown = drawdown.min() * 100
        
        volatility = monthly_returns.std() * np.sqrt(12) * 100
        
        start_date = df_clean["Date"].iloc[start_idx] if "Date" in df_clean.columns else df_clean.index[start_idx]
        end_date = df_clean["Date"].iloc[-1] if "Date" in df_clean.columns else df_clean.index[-1]
        
        start_str = start_date.strftime("%Y-%m") if hasattr(start_date, 'strftime') else str(start_date)[:7]
        end_str = end_date.strftime("%Y-%m") if hasattr(end_date, 'strftime') else str(end_date)[:7]
        
        return {
            "period": {
                "start": start_str,
                "end": end_str,
                "months": total_trades
            },
            "returns": {
                "strategy_return_pct": round(total_return, 2),
                "buy_hold_return_pct": round(buy_hold_return, 2),
                "excess_return_pct": round(total_return - buy_hold_return, 2)
            },
            "metrics": {
                "win_rate_pct": round(win_rate * 100, 1),
                "total_trades": total_trades,
                "correct_trades": int(correct_trades),
                "sharpe_ratio": round(sharpe, 2),
                "max_drawdown_pct": round(max_drawdown, 2),
                "volatility_pct": round(volatility, 2)
            },
            "final_capital": round(capital, 2),
            "history": self._format_history(results_df, df_clean),
            "improved": True
        }


def get_improved_prediction(monthly: pd.DataFrame) -> Dict[str, Any]:
    """
    ใช้ Improved Predictor แทนโมเดลเดิม
    """
    predictor = ImprovedPredictor()
    
    if not predictor.is_trained():
        raise ValueError("Model not trained")
    
    # Get improved prediction
    prediction, confidence, details = predictor.predict_with_trend_adjustment(monthly)
    
    # Get trend data
    trend_data = predictor.get_trend_analysis(monthly)
    
    # Get recommendation
    recommendation = predictor.get_recommendation_text(prediction, confidence, trend_data)
    
    return {
        "prediction": prediction,
        "confidence": confidence,
        "details": details,
        "trend": trend_data,
        "recommendation": recommendation,
        "improved": True
    }
