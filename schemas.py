from pydantic import BaseModel, Field
from typing import List, Optional

# -------- Request Schemas --------
class CompanyCreate(BaseModel):
    username: str
    company_name: str
    password: str
    company_email: str


class LoginRequest(BaseModel):
    username: str
    company_name: str
    password: str


class CompanyFilesUpdate(BaseModel):
    files: List[str]   # list of file names


# -------- File Schema --------
class FileInfo(BaseModel):
    pdf_name: str
    source: str
    filename: str
    parent_id: str


# -------- Response Schemas --------
class CompanyOut(BaseModel):
    id: int
    username: str
    company_name: str
    company_files_name: Optional[List[FileInfo]] = Field(default_factory=list)
    no_of_teams: int
    no_of_projects: int

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "simple"


class ChatRequest(BaseModel):
    message: str


# -------- Team Schemas --------
class TeamCreate(BaseModel):
    team_name: str
    team_password: str    


class TeamOut(BaseModel):
    id: int
    team_name: str
    team_files_name: Optional[List[dict]] = []

    class Config:
        orm_mode = True


# -------- Project Schemas --------
class ProjectCreate(BaseModel):
    project_name: str
    project_password: str


class ProjectOut(BaseModel):
    id: int
    project_name: str
    project_files_name: Optional[List[dict]] = []

    class Config:
        orm_mode = True


class ProjectMember(BaseModel):
    name: str
    role: str
    skills: List[str]


class ProjectInformation(BaseModel):
    project_description: Optional[str] = None
    no_project_members: Optional[int] = None
    project_members: Optional[List[ProjectMember]] = None
    techstack_or_tool: Optional[str] = None
    domain: Optional[str] = None
