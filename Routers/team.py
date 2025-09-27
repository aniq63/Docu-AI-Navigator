import uuid
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import shutil

import models, schemas

from Services.chat_services import extract_name_from_pdf, conversational_chain
from Routers.company import get_current_user, get_db
from Services.pdf_validator import document_validator
from Services.vectorstore import get_team_retriever , add_documents_to_team


router = APIRouter(
    prefix="/team",
    tags=["Team Management"]
)

@router.post('/team_register', response_model=schemas.TeamOut)
async def team_register(
    team_user: schemas.TeamCreate,
    current_user: models.Company = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure team name is unique within the company
    team_existing = db.query(models.Team).filter(
        models.Team.team_name == team_user.team_name,
        models.Team.company_id == current_user.id
    ).first()

    if team_existing:
        raise HTTPException(status_code=400, detail="Team name already exists for this company")
    
    team_obj = models.Team(
        team_name=team_user.team_name,
        team_password=team_user.team_password,
        company_id=current_user.id
    )

    db.add(team_obj)
    current_user.no_of_teams += 1
    db.commit()
    db.refresh(team_obj)
    db.refresh(current_user) 

    return team_obj

@router.post("/team_login", response_model=schemas.TeamOut)
async def team_login(
    team_name: str = Form(...),
    team_password: str = Form(...),
    current_user: models.Company = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find team under current company
    team = db.query(models.Team).filter(
        models.Team.team_name == team_name,
        models.Team.company_id == current_user.id
    ).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found under this company")

    # Verify password (plain text for now, hash later)
    if team.team_password != team_password:
        raise HTTPException(status_code=401, detail="Invalid team password")

    return team


@router.post("/team_upload", response_model=schemas.TeamOut)
async def team_upload(
    db: Session = Depends(get_db),
    current_user: models.Company = Depends(get_current_user),
    file: UploadFile = File(...),
    team_id: int = Form(...)
):
    # Validate team exists under current company
    team = db.query(models.Team).filter(
        models.Team.id == team_id,
        models.Team.company_id == current_user.id
    ).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found under this company")

    # Save PDF under company/team folder
    company_folder = os.path.join("uploads", f"company_{current_user.id}", f"team_{team_id}")
    os.makedirs(company_folder, exist_ok=True)

    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    saved_path = os.path.join(company_folder, unique_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load docs from PDF
    documents = document_validator(saved_path)
    sources = list({doc.metadata.get("source", "unknown") for doc in documents})
    source = sources[0] if sources else "unknown"

    # Extract PDF readable name
    extracted_name = extract_name_from_pdf(documents)

    # Add to team collection
    parent_id = add_documents_to_team(
        str(current_user.id),
        str(team.id),
        documents,
        file_name=unique_filename
    )

    # Store file metadata in team record (JSON-friendly dicts instead of strings)
    new_file_info = {
        "pdf_name": extracted_name,
        "source": source,
        "filename": unique_filename,
        "parent_id": parent_id
    }

    existing_files = team.team_files_name or []
    team.team_files_name = existing_files + [new_file_info]

    db.commit()
    db.refresh(team)

    return team


# --------------------- TEAM CHAT ---------------------
@router.post("/team_chat")
async def team_chat(
    message: str = Form(...),
    team_id: int = Form(...),
    current_user: models.Company = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate team exists under current company
    team = db.query(models.Team).filter(
        models.Team.id == team_id,
        models.Team.company_id == current_user.id
    ).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found under this company")

    try:
        company_id = str(current_user.id)
        team_id = str(team.id)

        # Build retriever
        retriever = get_team_retriever(company_id, team_id, k=5, fetch_k=20)
        chain = conversational_chain(retriever)

        result = chain.invoke({"question": message})
        answer = result["answer"]

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
