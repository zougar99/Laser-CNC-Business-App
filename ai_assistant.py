"""
AI Assistant - Smart AI features for LaserFlow
Provides intelligent suggestions, analysis, and automation
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from pathlib import Path


class AIAssistant:
    """AI Assistant for business intelligence and suggestions"""
    
    def __init__(self):
        self.config_path = Path("app_config.json")
        self._load_config()
    
    def _load_config(self):
        """Load AI configuration"""
        self.ai_enabled = False
        self.ai_provider = "local"  # local, openai, anthropic
        self.api_key = ""
        
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.ai_enabled = config.get("ai_enabled", False)
                    self.ai_provider = config.get("ai_provider", "local")
                    self.api_key = config.get("ai_api_key", "")
            except:
                pass
    
    def analyze_pricing(self, price: float, cost: float, minutes: float) -> List[str]:
        """Analyze pricing and return AI suggestions"""
        suggestions = []
        
        if price <= 0:
            suggestions.append("⚠️ السعر صفر أو سالب. يجب تحديد سعر صحيح.")
            return suggestions
        
        # Rule 1: Price less than cost
        if price < cost:
            suggestions.append("❌ السعر أقل من التكلفة! خسارة مؤكدة. يجب زيادة السعر.")
        
        # Rule 2: Low margin
        if cost > 0:
            margin_percent = ((price - cost) / price) * 100
            if 0 < margin_percent < 15:
                suggestions.append("⚠️ الهامش ضعيف ({:.1f}%). فكر في زيادة السعر قليلاً.".format(margin_percent))
            elif margin_percent < 0:
                suggestions.append("❌ خسارة! السعر أقل من التكلفة بمقدار {:.2f} MAD.".format(cost - price))
            elif margin_percent >= 50:
                suggestions.append("✅ هامش ممتاز ({:.1f}%)! سعر جيد.".format(margin_percent))
        
        # Rule 3: Time analysis
        if minutes > 120:
            suggestions.append("⚠️ الوقت طويل جداً ({:.0f} دقيقة). راجع المعاملات أو فكر في تقسيم العمل.".format(minutes))
        elif minutes < 5:
            suggestions.append("💡 وقت قصير ({:.0f} دقيقة). يمكنك زيادة السعر قليلاً.".format(minutes))
        
        # Rule 4: Rate per minute
        if minutes > 0:
            rate_per_min = price / minutes
            if rate_per_min < 5:
                suggestions.append("⚠️ السعر لكل دقيقة منخفض ({:.2f} MAD/min). فكر في زيادة السعر.".format(rate_per_min))
            elif rate_per_min > 20:
                suggestions.append("✅ سعر ممتاز لكل دقيقة ({:.2f} MAD/min)!".format(rate_per_min))
        
        return suggestions
    
    def analyze_business_health(self, revenue: float, expenses: float, jobs_count: int) -> Dict[str, Any]:
        """Analyze overall business health"""
        analysis = {
            "status": "unknown",
            "score": 0,
            "suggestions": [],
            "metrics": {}
        }
        
        if revenue <= 0:
            analysis["status"] = "no_data"
            analysis["suggestions"].append("لا توجد بيانات مالية للتحليل.")
            return analysis
        
        # Calculate profit
        profit = revenue - expenses
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
        
        # Calculate score (0-100)
        score = 0
        
        # Revenue score (0-30)
        if revenue > 50000:
            score += 30
        elif revenue > 20000:
            score += 20
        elif revenue > 10000:
            score += 10
        
        # Profit margin score (0-40)
        if profit_margin > 30:
            score += 40
        elif profit_margin > 20:
            score += 30
        elif profit_margin > 10:
            score += 20
        elif profit_margin > 0:
            score += 10
        
        # Jobs count score (0-30)
        if jobs_count > 100:
            score += 30
        elif jobs_count > 50:
            score += 20
        elif jobs_count > 20:
            score += 10
        
        analysis["score"] = score
        analysis["metrics"] = {
            "revenue": revenue,
            "expenses": expenses,
            "profit": profit,
            "profit_margin": profit_margin,
            "jobs_count": jobs_count
        }
        
        # Determine status
        if score >= 80:
            analysis["status"] = "excellent"
            analysis["suggestions"].append("✅ أداء ممتاز! استمر في هذا المستوى.")
        elif score >= 60:
            analysis["status"] = "good"
            analysis["suggestions"].append("✅ أداء جيد. يمكنك تحسين الأرباح أكثر.")
        elif score >= 40:
            analysis["status"] = "fair"
            analysis["suggestions"].append("⚠️ أداء متوسط. راجع التكاليف والأسعار.")
        else:
            analysis["status"] = "poor"
            analysis["suggestions"].append("❌ أداء ضعيف. راجع استراتيجية التسعير والتكاليف.")
        
        # Specific suggestions
        if profit_margin < 10:
            analysis["suggestions"].append("⚠️ هامش الربح منخفض ({:.1f}%). فكر في زيادة الأسعار أو تقليل التكاليف.".format(profit_margin))
        
        if expenses > revenue * 0.7:
            analysis["suggestions"].append("⚠️ التكاليف عالية جداً ({:.1f}% من الإيرادات). راجع المصروفات.".format((expenses/revenue)*100))
        
        if jobs_count > 0:
            avg_revenue_per_job = revenue / jobs_count
            if avg_revenue_per_job < 100:
                analysis["suggestions"].append("💡 متوسط الإيراد لكل مشروع منخفض ({:.2f} MAD). فكر في زيادة الأسعار.".format(avg_revenue_per_job))
        
        return analysis
    
    def suggest_optimization(self, jobs_data: List[Dict]) -> List[str]:
        """Suggest business optimizations based on jobs data"""
        suggestions = []
        
        if not jobs_data:
            suggestions.append("لا توجد بيانات للمشاريع. ابدأ بإضافة مشاريع.")
            return suggestions
        
        # Analyze jobs
        total_revenue = sum(j.get("revenue", 0) for j in jobs_data)
        total_minutes = sum(j.get("minutes", 0) for j in jobs_data)
        low_margin_count = 0
        high_time_count = 0
        
        for job in jobs_data:
            revenue = job.get("revenue", 0)
            cost = job.get("cost", 0)
            minutes = job.get("minutes", 0)
            
            if cost > 0 and revenue > 0:
                margin = ((revenue - cost) / revenue) * 100
                if margin < 15:
                    low_margin_count += 1
            
            if minutes > 60:
                high_time_count += 1
        
        # Generate suggestions
        if low_margin_count > len(jobs_data) * 0.3:
            suggestions.append("⚠️ {:.0f}% من المشاريع لديها هامش ضعيف. راجع استراتيجية التسعير.".format((low_margin_count/len(jobs_data))*100))
        
        if high_time_count > len(jobs_data) * 0.2:
            suggestions.append("💡 {:.0f}% من المشاريع تستغرق وقتاً طويلاً. فكر في تحسين العمليات.".format((high_time_count/len(jobs_data))*100))
        
        if total_minutes > 0:
            avg_rate = total_revenue / total_minutes
            if avg_rate < 7:
                suggestions.append("⚠️ متوسط السعر لكل دقيقة منخفض ({:.2f} MAD/min). فكر في زيادة الأسعار.".format(avg_rate))
            elif avg_rate > 15:
                suggestions.append("✅ متوسط السعر ممتاز ({:.2f} MAD/min)!".format(avg_rate))
        
        # Client analysis
        clients = {}
        for job in jobs_data:
            client_id = job.get("client_id")
            if client_id:
                if client_id not in clients:
                    clients[client_id] = {"jobs": 0, "revenue": 0}
                clients[client_id]["jobs"] += 1
                clients[client_id]["revenue"] += job.get("revenue", 0)
        
        if len(clients) > 0:
            top_client = max(clients.items(), key=lambda x: x[1]["revenue"])
            if top_client[1]["revenue"] > total_revenue * 0.5:
                suggestions.append("💡 عميل واحد يمثل أكثر من 50% من الإيرادات. فكر في تنويع قاعدة العملاء.")
        
        return suggestions
    
    def generate_report_summary(self, period: str, data: Dict) -> str:
        """Generate AI-powered report summary"""
        summary = f"تقرير {period}\n\n"
        
        revenue = data.get("revenue", 0)
        expenses = data.get("expenses", 0)
        profit = revenue - expenses
        jobs_count = data.get("jobs_count", 0)
        
        summary += f"📊 الإيرادات: {revenue:.2f} MAD\n"
        summary += f"💰 المصروفات: {expenses:.2f} MAD\n"
        summary += f"💵 صافي الربح: {profit:.2f} MAD\n"
        summary += f"📋 عدد المشاريع: {jobs_count}\n\n"
        
        if profit > 0:
            margin = (profit / revenue * 100) if revenue > 0 else 0
            summary += f"✅ هامش الربح: {margin:.1f}%\n"
            
            if margin > 30:
                summary += "🎉 أداء ممتاز! هامش ربح عالي.\n"
            elif margin > 20:
                summary += "✅ أداء جيد. استمر في هذا المستوى.\n"
            elif margin > 10:
                summary += "⚠️ هامش متوسط. يمكنك التحسين.\n"
            else:
                summary += "❌ هامش منخفض. راجع التكاليف والأسعار.\n"
        else:
            summary += "❌ خسارة! يجب مراجعة التكاليف والأسعار فوراً.\n"
        
        if jobs_count > 0:
            avg_revenue = revenue / jobs_count
            summary += f"\n💡 متوسط الإيراد لكل مشروع: {avg_revenue:.2f} MAD\n"
        
        return summary
    
    def predict_revenue(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Predict future revenue based on historical data"""
        if len(historical_data) < 3:
            return {
                "prediction": 0,
                "confidence": "low",
                "message": "لا توجد بيانات كافية للتنبؤ."
            }
        
        # Simple moving average prediction
        recent_revenues = [d.get("revenue", 0) for d in historical_data[-3:]]
        avg_revenue = sum(recent_revenues) / len(recent_revenues)
        
        # Growth trend (if available)
        if len(historical_data) >= 6:
            older_avg = sum([d.get("revenue", 0) for d in historical_data[-6:-3]]) / 3
            growth_rate = ((avg_revenue - older_avg) / older_avg * 100) if older_avg > 0 else 0
        else:
            growth_rate = 0
        
        predicted = avg_revenue * (1 + growth_rate / 100) if growth_rate > 0 else avg_revenue
        
        return {
            "prediction": predicted,
            "confidence": "medium" if len(historical_data) >= 6 else "low",
            "growth_rate": growth_rate,
            "message": f"التنبؤ: {predicted:.2f} MAD (نمو: {growth_rate:.1f}%)" if growth_rate > 0 else f"التنبؤ: {predicted:.2f} MAD"
        }
