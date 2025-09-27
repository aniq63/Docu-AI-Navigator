# Routers/company.py
from fastapi import APIRouter, HTTPException, Header, Depends, UploadFile, File, Request
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import and_
import os, shutil, uuid
import warnings
warnings.filterwarnings("ignore")

import models, schemas
from database import engine, Base, SessionLocal
from Services.chat_services import extract_name_from_pdf, conversational_chain
from Services.vectorstore import add_documents_to_collection, get_retriever_for_company
from Services.pdf_validator import document_validator

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/company",
    tags=["Company Management"]
)


# Dependency: database session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def home():
    return {"message": "Document Intelligent System for Companies"}


# -------------------- Authentication Dependency --------------------
def get_current_user(x_token: str = Header(None), db: Session = Depends(get_db)):
    if not x_token:
        raise HTTPException(status_code=401, detail="X-Token header missing")
    user = db.query(models.Company).filter(models.Company.session_token == x_token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Token")
    return user


# -------------------- Register (accept JSON or form-data) --------------------
@router.post("/register", response_model=schemas.CompanyOut, status_code=status.HTTP_201_CREATED)
async def register_company(request: Request, db: Session = Depends(get_db)):
    """
    Accepts either JSON body or form-data (multipart/form-data / x-www-form-urlencoded).
    Validates with schemas.CompanyCreate then creates company.
    """
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            payload = await request.json()
        else:
            form = await request.form()
            payload = dict(form)

        # Validate with Pydantic schema (ensures consistent field names)
        user = schemas.CompanyCreate(**payload)

    except Exception as e:
        # return readable error for invalid payload
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

    # Check duplicates
    existing_username = db.query(models.Company).filter(models.Company.username == user.username).first()
    existing_company = db.query(models.Company).filter(models.Company.company_name == user.company_name).first()
    existing_email = db.query(models.Company).filter(models.Company.company_email == user.company_email).first()

    if existing_username or existing_company or existing_email:
        raise HTTPException(status_code=400, detail="User with given username, company name, or email already exists")

    company_user = models.Company(
        username=user.username,
        company_name=user.company_name,
        password=user.password,
        company_email=user.company_email
    )

    db.add(company_user)
    db.commit()
    db.refresh(company_user)

    return company_user


# -------------------- Login (accept JSON or form-data) --------------------
@router.post("/login", response_model=schemas.TokenResponse)
async def company_login(request: Request, db: Session = Depends(get_db)):
    """
    Accepts JSON or form-data with fields: username, company_name, password
    """
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            payload = await request.json()
        else:
            form = await request.form()
            payload = dict(form)

        form_obj = schemas.LoginRequest(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

    user = db.query(models.Company).filter(
        and_(
            models.Company.username == form_obj.username,
            models.Company.company_name == form_obj.company_name
        )
    ).first()

    if not user or user.password != form_obj.password:
        raise HTTPException(status_code=401, detail="Incorrect username, company name, or password")

    token = uuid.uuid4().hex
    user.session_token = token
    db.commit()

    return {"access_token": token, "token_type": "simple"}


# -------------------- Protected: Get Current User --------------------
@router.get("/me", response_model=schemas.CompanyOut)
def read_me(current_user: models.Company = Depends(get_current_user)):
    return current_user


# -------------------- Logout --------------------
@router.post("/logout")
def logout(current_user: models.Company = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.session_token = None
    db.commit()
    return {"message": "Logged out"}


# -------------------- Upload PDF + create embeddings --------------------
@router.post("/upload_pdf", response_model=schemas.CompanyOut)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: models.Company = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        company_folder = os.path.join("uploads", f"company_{current_user.id}")
        os.makedirs(company_folder, exist_ok=True)

        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        saved_path = os.path.join(company_folder, unique_filename)

        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        documents = document_validator(saved_path)
        sources = list({doc.metadata.get("source", "unknown") for doc in documents})
        source = sources[0] if sources else "unknown"

        extracted_name = extract_name_from_pdf(documents)

        parent_id = add_documents_to_collection(str(current_user.id), documents, file_name=unique_filename)

        extracted_info = {
            "pdf_name": extracted_name,
            "source": source,
            "filename": unique_filename,
            "parent_id": parent_id
        }
        existing_files = current_user.company_files_name or []
        current_user.company_files_name = existing_files + [extracted_info]

        db.commit()
        db.refresh(current_user)

        return current_user

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------- Chat endpoint (per-company retrieval) --------------------
@router.post("/chat")
async def chat_endpoint(
    chat: schemas.ChatRequest,
    current_user: models.Company = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        company_id = str(current_user.id)
        retriever = get_retriever_for_company(company_id, k=5, fetch_k=20)
        chain = conversational_chain(retriever)

        result = chain.invoke({"question": chat.message})
        answer = result["answer"]

        # optionally include sources if you want; keeping minimal to match prior behavior
        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
