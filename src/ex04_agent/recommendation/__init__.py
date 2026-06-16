"""Recommendation generation package."""

from ex04_agent.recommendation.engine import RecommendationEngine
from ex04_agent.recommendation.model import ArchitectureRecommendation, PatchPlanItem
from ex04_agent.recommendation.report_writer import RecommendationSummary

__all__ = ["ArchitectureRecommendation", "PatchPlanItem", "RecommendationEngine", "RecommendationSummary"]
