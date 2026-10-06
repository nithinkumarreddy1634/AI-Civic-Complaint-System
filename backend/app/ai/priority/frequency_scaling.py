"""Sub-linear saturating frequency scaler for civic complaint prioritization."""
from typing import Dict
from app.ai.priority.config import FrequencyScalingConfig, priority_config


class FrequencyScaler:
    """Transforms raw complaint report count (duplicate frequency) into a bounded 0-100 score."""

    def __init__(self, config: FrequencyScalingConfig = None):
        self.config = config or priority_config.frequency_scaling

    def scale(self, report_count: int) -> float:
        """Calculate normalized frequency score from raw report count.

        A sub-linear piecewise function provides diminishing marginal returns:
        - 1 report   -> 15.0
        - 2 reports  -> 28.0
        - 3 reports  -> 40.0
        - 5 reports  -> 60.0
        - 8 reports  -> 75.0
        - 10 reports -> 85.0
        - 15 reports -> 95.0
        - 20+ reports-> 100.0 (saturated)

        This prevents organized or automated duplicate flooding from unilaterally
        escalating low-severity issues into URGENT tiers.
        """
        if report_count <= 0:
            return 0.0

        if report_count >= self.config.saturation_cap:
            return 100.0

        bps = sorted(self.config.breakpoints.items(), key=lambda x: x[0])
        
        # If below or at minimum breakpoint
        if report_count <= bps[0][0]:
            return bps[0][1]

        # Interpolate between matching breakpoints
        for i in range(len(bps) - 1):
            c1, s1 = bps[i]
            c2, s2 = bps[i + 1]
            if c1 <= report_count <= c2:
                fraction = (report_count - c1) / (c2 - c1)
                score = s1 + fraction * (s2 - s1)
                return round(score, 2)

        return 100.0


frequency_scaler = FrequencyScaler()
