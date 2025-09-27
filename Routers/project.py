# project_router.py
import uuid
import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

import models, schemas
from Services.chat_services import extract_name_from_pdf, conversational_chain, build_project_plan
from Routers.company import get_current_user, get_db
from Services.pdf_validator import document_validator
from Services.vectorstore import add_documents_to_project, get_project_retriever

router = APIRouter(
    prefix="/project",
    tags=["Project Management"]
)

# --------------------- REGISTER PROJECT ---------------------
@router.post("/project_register", response_model=schemas.ProjectOut)
async def register_project(
    project: schemas.ProjectCreate,
    current_user: models.Company = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure project name is unique within the company
    existing_project = db.query(models.Project).filter(
        models.Project.project_name == project.project_name,
        models.Project.company_id == current_user.id
    ).first()

    if existing_project:
        raise HTTPException(status_code=400, detail="Project name already exists for this company")

    project_obj = models.Project(
        project_name=project.project_name,
        project_password=project.project_password,
        company_id=current_user.id
    )

    db.add(project_obj)
    current_user.no_of_projects +=1
    db.commit()
    db.refresh(project_obj)
    db.refresh(current_user) 

    return project_obj

# --------------------- LOGIN PROJECT (ADDED CODE) ---------------------
@router.post("/project_login", response_model=schemas.ProjectOut)
async def project_login(
    project_name: str = Form(...),
    project_password: str = Form(...),
    current_user: models.Company = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handles the login request for a specific project under a logged-in company.
    """
    # Find the project under the current logged-in company
    project = db.query(models.Project).filter(
        models.Project.project_name == project_name,
        models.Project.company_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found under this company")

    # Verify the password (ensure this matches your registration method, e.g., hashing in production)
    if project.project_password != project_password:
        raise HTTPException(status_code=401, detail="Invalid project password")

    return project


# --------------------- UPLOAD DOCS TO PROJECT ---------------------
@router.post("/upload_project_pdf", response_model=schemas.ProjectOut)
async def upload_project_docs(
    db: Session = Depends(get_db),
    current_user: models.Company = Depends(get_current_user),
    file: UploadFile = File(...),
    project_id: int = Form(...)
):
    # Validate project exists under current company
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.company_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found under this company")

    # Save file under company/project folder
    project_folder = os.path.join("uploads", f"company_{current_user.id}", f"project_{project_id}")
    os.makedirs(project_folder, exist_ok=True)

    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    saved_path = os.path.join(project_folder, unique_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load docs from file
    documents = document_validator(saved_path)
    sources = list({doc.metadata.get("source", "unknown") for doc in documents})
    source = sources[0] if sources else "unknown"

    # Extract readable name
    extracted_name = extract_name_from_pdf(documents)

    # Add to vectorstore
    parent_id = add_documents_to_project(
        str(current_user.id),
        str(project.id),
        documents,
        file_name=unique_filename
    )

    # Save metadata in DB
    new_file_info = {
        "pdf_name": extracted_name,
        "source": source,
        "filename": unique_filename,
        "parent_id": parent_id
    }

    existing_files = project.project_files_name or []
    project.project_files_name = existing_files + [new_file_info]

    db.commit()
    db.refresh(project)

    return project


# --------------------- PROJECT CHAT ---------------------
@router.post("/project_chat")
async def project_chat(
    chat: schemas.ChatRequest,
    project_id: int = Form(...),
    current_user: models.Company = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate project exists under current company
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.company_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found under this company")

    try:
        company_id = str(current_user.id)
        project_id_str = str(project.id)

        retriever = get_project_retriever(company_id, project_id_str, k=5, fetch_k=20)
        chain = conversational_chain(retriever)

        result = chain.invoke({"question": chat.message})
        answer = result["answer"]

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    

@router.post("/project_information")
async def project_information(
    project_id: int,
    project_info: schemas.ProjectInformation,
    current_user: models.Company = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # validate project
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.company_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # update project
    project.project_description = project_info.project_description
    project.no_project_members = project_info.no_project_members
    project.project_members = [member.dict() for member in (project_info.project_members or [])]
    project.techstack_or_tool = project_info.techstack_or_tool
    project.domain = project_info.domain

    db.commit()
    db.refresh(project)

    return {"message": "Project info updated successfully", "project": project_info}
    


@router.post("/plan")
async def generate_project_plan(
    project_id: int = Form(...),
    current_user: models.Company = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Ensure the project exists under this company
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.company_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found under this company")

    try:
        result = build_project_plan(
            domain=project.domain or "",
            project_name=project.project_name,
            no_project_members=project.no_project_members or 0,
            project_members=project.project_members or [],
            techstack_tools=project.techstack_or_tool or "",
            project_description=project.project_description or ""
        )

        if hasattr(result, "dict"):
            result = result.dict()

        return {
            "project_id": project.id,
            "project_name": project.project_name,
            "plan": result  # structured JSON, easy for frontend
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating project plan: {str(e)}")