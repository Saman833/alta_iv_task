from fastapi import APIRouter
from services.analytics_service import AnalyticsService
from services.autonomous_analytics_service import AutonomousAnalyticsService
from deps import SessionDep
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["analytics"], prefix="/analytics")

class AnalyticsRequest(BaseModel):
    user_input: Optional[str] = None
    question: Optional[str] = None
    context_info: Optional[dict] = None

@router.post("/analyze")
async def analyze_request(request: AnalyticsRequest, db: SessionDep):
    analytics_service = AnalyticsService(db)
    user_input = request.user_input or request.question
    if not user_input:
        return {"error": "Either user_input or question is required"}
    return analytics_service.analyze_user_request(user_input, request.context_info)

# New endpoint for user-facing analytics Q&A
def get_final_user_response(result):
    # Try to extract the final user response from the analytics pipeline result
    if isinstance(result, dict):
        # Try the new key
        if "final_user_response" in result:
            return {"final_user_response": result["final_user_response"]}
        # Fallback: try comprehensive synthesis
        if "comprehensive_research" in result:
            return {"final_user_response": result["comprehensive_research"].get("expected_comprehensive_answer", "No answer generated.")}
    return {"final_user_response": "No answer generated."}

@router.post("/ask")
async def ask_analytics(request: AnalyticsRequest, db: SessionDep):
    user_input = request.user_input or request.question
    if not user_input:
        return {"error": "Either user_input or question is required"}
    
    analytics_service = AutonomousAnalyticsService(db)
    result = analytics_service.analyze_user_request_autonomously(user_input)
    
    # Extract only the final user response text
    if isinstance(result, dict) and "final_user_response" in result:
        return {"answer": result["final_user_response"]}
    else:
        return {"answer": "Unable to generate answer. Please try again."} 