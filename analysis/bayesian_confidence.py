"""
Bayesian uncertainty quantification for confidence estimation
"""

import numpy as np
from typing import Dict, List, Tuple
import logging
from scipy import stats

logger = logging.getLogger(__name__)


class BayesianConfidenceEstimator:
    """Implements Bayesian uncertainty quantification"""
    
    def __init__(self, n_samples: int = 20):
        self.n_samples = n_samples
    
    def calculate_confidence_with_uncertainty(self,
                                             mapping_scores: List[float],
                                             edge_case_scores: Dict[str, float],
                                             dropout_rate: float = 0.1) -> Tuple[float, Dict]:
        """Calculate confidence with epistemic and aleatoric uncertainty"""
        
        # Monte Carlo dropout sampling
        predictions = []
        for _ in range(self.n_samples):
            # Simulate dropout by randomly masking features
            masked_scores = self._apply_dropout(mapping_scores, dropout_rate)
            prediction = self._calculate_base_confidence(masked_scores, edge_case_scores)
            predictions.append(prediction)
        
        predictions = np.array(predictions)
        
        # Calculate uncertainties
        mean_confidence = np.mean(predictions)
        epistemic_uncertainty = np.std(predictions)  # Model uncertainty
        
        # Estimate aleatoric uncertainty from data variance
        aleatoric_uncertainty = self._estimate_aleatoric_uncertainty(
            mapping_scores, edge_case_scores
        )
        
        # Total uncertainty
        total_uncertainty = np.sqrt(
            epistemic_uncertainty**2 + aleatoric_uncertainty**2
        )
        
        # Calibrated confidence (with uncertainty adjustment)
        calibrated_confidence = mean_confidence * (1 - min(0.3, total_uncertainty))
        
        # Calculate confidence interval
        confidence_interval = stats.t.interval(
            0.95, len(predictions)-1,
            loc=mean_confidence,
            scale=epistemic_uncertainty/np.sqrt(len(predictions))
        )
        
        return calibrated_confidence, {
            "mean_confidence": mean_confidence,
            "epistemic_uncertainty": epistemic_uncertainty,
            "aleatoric_uncertainty": aleatoric_uncertainty,
            "total_uncertainty": total_uncertainty,
            "confidence_interval": confidence_interval,
            "samples": predictions.tolist()
        }
    
    def _apply_dropout(self, scores: List[float], rate: float) -> List[float]:
        """Apply dropout to scores"""
        mask = np.random.binomial(1, 1-rate, len(scores))
        return [s * m / (1-rate) for s, m in zip(scores, mask)]
    
    def _calculate_base_confidence(self, scores: List[float], edge_cases: Dict) -> float:
        """Calculate base confidence from scores"""
        if not scores:
            return 0.0
        
        base = np.mean(scores)
        
        # Adjust for edge cases
        if "context_imbalance" in edge_cases:
            base *= (1 - edge_cases["context_imbalance"] * 0.2)
        if "outdated_content" in edge_cases:
            base *= (1 - edge_cases["outdated_content"] * 0.15)
        
        return min(1.0, max(0.0, base))
    
    def _estimate_aleatoric_uncertainty(self, scores: List[float], edge_cases: Dict) -> float:
        """Estimate inherent data uncertainty"""
        if not scores:
            return 0.5
        
        # Base uncertainty from score variance
        score_variance = np.var(scores) if len(scores) > 1 else 0.1
        
        # Increase uncertainty for edge cases
        edge_case_penalty = len(edge_cases) * 0.05
        
        return min(0.5, score_variance + edge_case_penalty)
    
    def get_confidence_interpretation(self, uncertainty_results: Dict) -> str:
        """Interpret confidence results"""
        total_unc = uncertainty_results["total_uncertainty"]
        conf_interval = uncertainty_results["confidence_interval"]
        
        if total_unc < 0.1:
            reliability = "HIGH"
            interpretation = "Very reliable prediction"
        elif total_unc < 0.2:
            reliability = "MODERATE"
            interpretation = "Moderately reliable prediction"
        else:
            reliability = "LOW"
            interpretation = "Uncertain prediction - manual review recommended"
        
        return f"{interpretation} (95% CI: [{conf_interval[0]:.2f}, {conf_interval[1]:.2f}])"