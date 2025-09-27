from fastapi import FastAPI
from Routers.company import router as company_router
from Routers.team import router as team_router
from Routers.project import router as project_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="Document Intelligent System for Companies")
app.include_router(company_router)
app.include_router(team_router)
app.include_router(project_router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Allow your frontend origin (change origin accordingly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:8000", "*"],  # '*' for development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
