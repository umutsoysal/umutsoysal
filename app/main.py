from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Umut Soysal Portfolio API",
    description="Personal portfolio API showcasing skills and projects",
    version="1.0.0",
)

PROFILE = {
    "name": "Umut Soysal",
    "bio": (
        "A software developer with an MSc. Degree in engineering from Carnegie Mellon University. "
        "Passionate about building smart and scalable production grade applications."
    ),
    "education": "Carnegie Mellon University - MSc Engineering",
}

SKILLS = [
    {"name": "Python", "category": "language"},
    {"name": "CSharp", "category": "language"},
    {"name": "Flutter", "category": "framework"},
    {"name": "FastAPI", "category": "framework"},
    {"name": "AWS", "category": "cloud"},
    {"name": "Docker", "category": "devops"},
]

PROJECTS: List[dict] = []


class Project(BaseModel):
    name: str
    description: str
    tech_stack: List[str]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/profile")
def get_profile():
    return PROFILE


@app.get("/skills")
def get_skills():
    return {"skills": SKILLS}


@app.get("/skills/{category}")
def get_skills_by_category(category: str):
    filtered = [s for s in SKILLS if s["category"] == category]
    if not filtered:
        raise HTTPException(status_code=404, detail=f"No skills found for category '{category}'")
    return {"category": category, "skills": filtered}


@app.get("/projects")
def get_projects():
    return {"projects": PROJECTS}


@app.post("/projects", status_code=201)
def create_project(project: Project):
    new_project = project.model_dump()
    PROJECTS.append(new_project)
    return new_project
