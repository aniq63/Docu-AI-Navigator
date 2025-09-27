# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True, index=True)  # team_id
    team_name = Column(String, unique=False, nullable=False)  # unique per company, not global
    team_password = Column(String, nullable=False)
    team_files_name = Column(JSON, nullable=True, default=list)

    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    company = relationship("Company", back_populates="teams")


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    company_name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    company_email = Column(String, unique=True, nullable=False)
    session_token = Column(String, index=True, nullable=True)
    company_files_name = Column(JSON, nullable=True, default=list)
    no_of_teams = Column(Integer, nullable=False, default=0)
    no_of_projects = Column(Integer, nullable=False, default=0)

    teams = relationship("Team", back_populates="company", cascade="all, delete")
    projects = relationship("Project", back_populates="company", cascade="all, delete")

class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False, unique=True)
    project_password = Column(String, nullable=False)
    project_files_name = Column(JSON, nullable=True, default=list)
    project_description = Column(String, nullable=True)
    no_project_members = Column(Integer, nullable=True)
    project_members = Column(JSON, nullable=True, default=list)
    techstack_or_tool = Column(String, nullable=True)
    domain = Column(String, nullable=True)

    company_id = Column(Integer, ForeignKey("company.id"), nullable=False) 
    company = relationship("Company", back_populates="projects")




    



