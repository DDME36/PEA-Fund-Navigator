"""
Risk Management System
ป้องกันการขาดทุนหนักเมื่อทายผิด
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class RiskManager:
    """
    จัดการความเสี่ยง:
    1. Position Sizing based on Confidence
    2. Volatility-based Adjustment
    3. Max Allocation Limit
    4. Drawdown Protection
    """
    
    def __init__(
        self,
        max_allocation: float = 0.80,  # ไม่เกิน 80%
        min_confidence: float = 0.60,  # ต้องมั่นใจอย่างน้อย 60%
        volatility_threshold: float = 15.0,  # ถ้า vol > 15% ลดสัดส่วน
    ):
        self.max_allocation = max_allocation
        self.min_confidence = min_confidence
        self.volatility_threshold = volatility_threshold
    
    def calculate_safe_allocation(
        self,
        prediction: int,
        confidence: float,
        volatility: float,
        drawdown: float,
        trend_score: float
    ) -> Tuple[float, str]:
        """
        คำนวณสัดส่วนที่ปลอดภัย
        
        Returns:
            (allocation, reason)
        """
        reasons = []
        
        # Base allocation from confidence
        if prediction == 1:  # Bullish
            if confidence < self.min_confidence:
                base_alloc = 0.3
                reasons.append(f"Confidence ต่ำ ({confidence:.1%})")
            elif confidence < 0.65:
                base_alloc = 0.5
                reasons.append(f"Confidence ปานกลาง ({confidence:.1%})")
            elif confidence < 0.75:
                base_alloc = 0.7
                reasons.append(f"Confidence ดี ({confidence:.1%})")
            else:
                base_alloc = 0.85
                reasons.append(f"Confidence สูง ({confidence:.1%})")
        else:  # Bearish
            if confidence < self.min_confidence:
                base_alloc = 0.5
            elif confidence < 0.65:
                base_alloc = 0.4
            elif confidence < 0.75:
                base_alloc = 0.2
            else:
                base_alloc = 0.1
            reasons.append(f"Bearish signal ({confidence:.1%})")
        
        # Adjust for volatility
        if volatility > self.volatility_threshold:
            vol_penalty = (volatility - self.volatility_threshold) / 100
            base_alloc *= (1 - vol_penalty)
            reasons.append(f"High volatility ({volatility:.1f}%) → ลด {vol_penalty*100:.0f}%")
        
        # Adjust for drawdown
        if drawdown < -20:  # Deep drawdown
            # ถ้า drawdown ลึก อาจเป็นโอกาส (contrarian)
            if prediction == 1:  # Bullish
                base_alloc *= 1.1  # เพิ่มนิดหน่อย
                reasons.append(f"Deep drawdown ({drawdown:.1f}%) → oversold")
        elif drawdown > -5:  # Near peak
            # ถ้าใกล้จุดสูงสุด ระวัง
            base_alloc *= 0.9
            reasons.append(f"Near peak ({drawdown:.1f}%) → ระมัดระวัง")
        
        # Adjust for trend
        if trend_score < 30 and prediction == 1:  # Bullish แต่ trend ลง
            base_alloc *= 0.8
            reasons.append(f"Trend ขัดแย้ง (score {trend_score}) → ลด 20%")
        elif trend_score > 70 and prediction == 0:  # Bearish แต่ trend ขึ้น
            base_alloc *= 1.2  # ไม่ลดมากเกินไป
            reasons.append(f"Trend ขัดแย้ง (score {trend_score}) → ปรับ")
        
        # Apply max limit
        final_alloc = min(base_alloc, self.max_allocation)
        if final_alloc == self.max_allocation and base_alloc > self.max_allocation:
            reasons.append(f"จำกัดไม่เกิน {self.max_allocation*100:.0f}%")
        
        # Ensure minimum
        final_alloc = max(final_alloc, 0.0)
        
        reason_text = " | ".join(reasons)
        return final_alloc, reason_text
    
    def get_allocation_with_risk_management(
        self,
        prediction: int,
        confidence: float,
        market_data: Dict
    ) -> Dict:
        """
        คำนวณสัดส่วนพร้อม risk management
        """
        volatility = market_data.get("volatility", 10)
        drawdown = market_data.get("drawdown", 0)
        trend_score = market_data.get("trend_score", 50)
        
        allocation, reason = self.calculate_safe_allocation(
            prediction, confidence, volatility, drawdown, trend_score
        )
        
        return {
            "allocation": round(allocation * 100),
            "allocation_decimal": allocation,
            "reason": reason,
            "risk_adjusted": True,
            "original_confidence": confidence,
            "volatility": volatility,
            "drawdown": drawdown,
            "trend_score": trend_score
        }


def apply_risk_management(
    prediction: int,
    confidence: float,
    ml_features: Dict,
    trend_data: Dict
) -> Dict:
    """
    Helper function สำหรับใช้ใน daily_update.py
    """
    risk_manager = RiskManager(
        max_allocation=0.80,  # ไม่เกิน 80%
        min_confidence=0.60,
        volatility_threshold=15.0
    )
    
    market_data = {
        "volatility": ml_features.get("Volatility_3m", 10),
        "drawdown": ml_features.get("Drawdown", 0),
        "trend_score": trend_data.get("trend_score", 50)
    }
    
    return risk_manager.get_allocation_with_risk_management(
        prediction, confidence, market_data
    )
