from fastapi import FastAPI, Query
from pydantic import BaseModel
from market_analyser import MarketAnalyser

# Initialize FastAPI app
app = FastAPI()

# Initialize the MarketAnalyser instance
market_analyser = MarketAnalyser()

# Pydantic model for the API response
class MarketAnalysisResponse(BaseModel):
    summary: str

@app.get("/analyze", response_model=MarketAnalysisResponse)
async def analyze_market(query: str = Query(..., description="Market query to search for news articles"),
                         limit: int = Query(20, description="Number of news articles to retrieve")):
    """
    Analyze market trends based on the provided query.
    """
    try:
        # Call the analyze_market method of MarketAnalyser
        summary = market_analyser.analyze_market(query=query, limit=limit)
        return MarketAnalysisResponse(summary=summary)
    except Exception as e:
        return {"error": str(e)}

# Run this script using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
