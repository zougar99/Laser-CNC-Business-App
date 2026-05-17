# -*- coding: utf-8 -*-
"""
AI Risk Engine - طبقة AI
Offline, sklearn (RandomForest/LogisticRegression)
risk_score 0-100, classification (benign/suspicious/malware-likely), explainability
"""

import os
import json
import pickle

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except (ImportError, OSError):
    NUMPY_AVAILABLE = False
    np = None

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except (ImportError, OSError):
    # OSError/FileNotFoundError: vcomp140.dll missing (VC++ Redistributable)
    SKLEARN_AVAILABLE = False
    RandomForestClassifier = None
    LogisticRegression = None
    StandardScaler = None

from feature_extractor import extract_features, features_to_vector

FEATURE_NAMES = [
    'size_kb', 'entropy', 'location_risk', 'is_executable', 'double_ext', 'suspicious_name',
    'pe_sections', 'pe_imports_count', 'suspicious_imports', 'timestamp_anomaly'
]

REASON_LABELS = {
    'size_kb': 'File size unusual',
    'entropy': 'High entropy (packed/obfuscated)',
    'location_risk': 'Located in Downloads/Temp',
    'is_executable': 'Executable file type',
    'double_ext': 'Double extension detected',
    'suspicious_name': 'Suspicious filename pattern',
    'pe_sections': 'PE section count',
    'pe_imports_count': 'PE imports',
    'suspicious_imports': 'Suspicious API imports',
    'timestamp_anomaly': 'Timestamp anomaly',
}


class AIRiskEngine:
    """
    AI Risk Engine - Offline, sklearn
    Output: risk_score 0-100, classification, top_reasons (explainability)
    """

    def __init__(self, model_path='ai_risk_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = FEATURE_NAMES
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                self.model = data.get('model')
                self.scaler = data.get('scaler')
            except Exception:
                pass
        if self.model is None and SKLEARN_AVAILABLE and NUMPY_AVAILABLE:
            try:
                self.model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10)
                self.scaler = StandardScaler()
            except Exception:
                pass

    def predict(self, file_path):
        """
        Returns: {
            'risk_score': 0-100,
            'classification': 'benign'|'suspicious'|'malware-likely',
            'reasons': [top 5 reasons],
            'is_threat': bool (suspicious or malware-likely)
        }
        """
        feats = extract_features(file_path)
        vec = features_to_vector(feats)
        result = {
            'risk_score': 0,
            'classification': 'benign',
            'reasons': [],
            'is_threat': False,
        }

        # Rule-based fallback (no sklearn, no trained model, or model not fitted)
        model_ok = (self.model is not None and hasattr(self.model, 'classes_') and
                    len(getattr(self.model, 'classes_', [])) > 0)
        if not model_ok:
            score = self._rule_based_score(feats)
            result['risk_score'] = score
            result['classification'] = 'benign' if score < 30 else ('suspicious' if score < 70 else 'malware-likely')
            result['reasons'] = self._rule_based_reasons(feats)
            result['is_threat'] = score >= 30
            return result

        # ML prediction (model is fitted)
        try:
            X = np.array([vec], dtype=np.float64)
            if self.scaler and hasattr(self.scaler, 'mean_') and self.scaler.mean_ is not None:
                X = self.scaler.transform(X)
            proba = self.model.predict_proba(X)[0]
            if len(proba) == 2:
                risk_score = int(proba[1] * 100)
            else:
                risk_score = int(max(proba) * 100)
            result['risk_score'] = min(100, max(0, risk_score))
            result['classification'] = 'benign' if risk_score < 30 else ('suspicious' if risk_score < 70 else 'malware-likely')
            result['is_threat'] = risk_score >= 30

            # Explainability: feature importance
            if hasattr(self.model, 'feature_importances_'):
                imp = self.model.feature_importances_
                idx = np.argsort(imp)[::-1][:5]
                for i in idx:
                    if feats.get(FEATURE_NAMES[i], 0) != 0:
                        result['reasons'].append(REASON_LABELS.get(FEATURE_NAMES[i], FEATURE_NAMES[i]))
            if not result['reasons']:
                result['reasons'] = self._rule_based_reasons(feats)
        except Exception:
            result['risk_score'] = self._rule_based_score(feats)
            result['classification'] = 'benign' if result['risk_score'] < 30 else 'suspicious'
            result['reasons'] = self._rule_based_reasons(feats)
            result['is_threat'] = result['risk_score'] >= 30

        return result

    def _rule_based_score(self, feats):
        score = 0
        if feats.get('double_ext'):
            score += 40
        if feats.get('suspicious_name'):
            score += 35
        if feats.get('suspicious_imports', 0) > 0:
            score += 25 * min(feats['suspicious_imports'], 3)
        if feats.get('entropy', 0) > 7.5:
            score += 20
        if feats.get('location_risk') and feats.get('is_executable'):
            score += 25
        if feats.get('is_executable'):
            score += 5
        return min(95, score)

    def _rule_based_reasons(self, feats):
        reasons = []
        if feats.get('double_ext'):
            reasons.append('Double extension detected')
        if feats.get('suspicious_name'):
            reasons.append('Suspicious filename pattern')
        if feats.get('suspicious_imports', 0) > 0:
            reasons.append('Suspicious API imports')
        if feats.get('entropy', 0) > 7.5:
            reasons.append('High entropy (packed/obfuscated)')
        if feats.get('location_risk') and feats.get('is_executable'):
            reasons.append('Executable in Downloads/Temp')
        if feats.get('is_executable') and not reasons:
            reasons.append('Executable file type')
        return reasons[:5]
