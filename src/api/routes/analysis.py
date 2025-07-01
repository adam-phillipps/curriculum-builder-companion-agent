"""
Analysis API routes for gap analysis and content insights.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.services.gap_analysis import gap_analysis_service
from src.api.schemas.gap_analysis import (
    GapAnalysisSchema,
    PathwayGapAnalysisRequest,
    DomainGapAnalysisRequest,
    GapAnalysisSummary
)

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post(
    "/pathway-gaps",
    response_model=GapAnalysisSchema,
    summary="Analyze gaps in a learning pathway",
    description="Identify missing prerequisites and weak support areas in a specific learning pathway"
)
async def analyze_pathway_gaps(
    request: PathwayGapAnalysisRequest,
    db: AsyncSession = Depends(get_db)
) -> GapAnalysisSchema:
    """Analyze gaps in a specific learning pathway."""
    try:
        analysis = await gap_analysis_service.analyze_pathway_gaps(
            db=db,
            pathway_id=request.pathway_id
        )
        return GapAnalysisSchema(
            pathway_id=analysis.pathway_id,
            target_persona=analysis.target_persona,
            end_goal=analysis.end_goal,
            gaps=[gap.__dict__ for gap in analysis.gaps],
            pathway_strength=analysis.pathway_strength,
            total_missing_prerequisites=analysis.total_missing_prerequisites,
            weak_support_areas=analysis.weak_support_areas,
            weighted_gap_score=analysis.weighted_gap_score,
            critical_gaps=analysis.critical_gaps,
            gap_distribution=analysis.gap_distribution
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gap analysis failed: {str(e)}"
        )

@router.post(
    "/domain-gaps",
    response_model=GapAnalysisSchema,
    summary="Analyze gaps in a learning domain",
    description="Identify missing prerequisites and weak support areas for specific learning objectives"
)
async def analyze_domain_gaps(
    request: DomainGapAnalysisRequest,
    db: AsyncSession = Depends(get_db)
) -> GapAnalysisSchema:
    """Analyze gaps in a general learning domain."""
    try:
        analysis = await gap_analysis_service.analyze_domain_gaps(
            db=db,
            persona=request.persona,
            learning_objectives=request.learning_objectives
        )
        return GapAnalysisSchema(
            pathway_id=analysis.pathway_id,
            target_persona=analysis.target_persona,
            end_goal=analysis.end_goal,
            gaps=[gap.__dict__ for gap in analysis.gaps],
            pathway_strength=analysis.pathway_strength,
            total_missing_prerequisites=analysis.total_missing_prerequisites,
            weak_support_areas=analysis.weak_support_areas,
            weighted_gap_score=analysis.weighted_gap_score,
            critical_gaps=analysis.critical_gaps,
            gap_distribution=analysis.gap_distribution
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Domain gap analysis failed: {str(e)}"
        )

@router.get(
    "/gap-summary",
    response_model=GapAnalysisSummary,
    summary="Get gap analysis summary",
    description="Get overall summary of gap analysis across all pathways"
)
async def get_gap_analysis_summary(
    db: AsyncSession = Depends(get_db)
) -> GapAnalysisSummary:
    """Get summary of gap analysis across all pathways."""
    try:
        # This would be implemented to analyze all pathways
        # For now, return a placeholder response
        return GapAnalysisSummary(
            total_pathways_analyzed=0,
            total_gaps_found=0,
            missing_prerequisites=0,
            weak_support_areas=0,
            average_pathway_strength=0.0,
            average_weighted_gap_score=0.0,
            top_missing_concepts=[],
            recommendations_by_priority=[],
            critical_gap_distribution={}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gap summary failed: {str(e)}"
        )