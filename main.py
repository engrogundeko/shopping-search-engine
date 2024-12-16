from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.route import router

app = FastAPI(
    title="Search Engine API",
    version="0.1.0",
    description="API for performing advanced search across multiple providers",
)

app.include_router(router)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Volera API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)