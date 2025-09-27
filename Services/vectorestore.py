from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import uuid


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )


# --------------------- COMPANY VECTORSTORE ---------------------


# Add documents (PDF) to a company-scoped Chroma collection (called at upload time)
def add_documents_to_collection(company_id: str, documents, file_name: str = None):
    """
    - Splits `documents` into child chunks,
    - tags each chunk with metadata: company_id, parent_id, source (file_name),
    - adds them to Chroma collection: `company_{company_id}_chunks`.
    Returns generated parent_id for reference.
    """
    # Use a child splitter (fine-grained chunks)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
    child_docs = child_splitter.split_documents(documents)

    parent_id = str(uuid.uuid4())
    for d in child_docs:
        # tag metadata so retrieval can be filtered or used by LLM
        d.metadata["company_id"] = str(company_id)
        d.metadata["parent_id"] = parent_id
        if file_name:
            d.metadata["source"] = file_name

    embeddings = get_embeddings()
    collection_name = f"company_{company_id}_chunks"

    # Chroma client pointing to the shared persist directory; collection isolates per-company data
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_store"
    )

    # add_documents appends; it doesn't clobber other collections
    vectorstore.add_documents(child_docs)

    # persist to disk so the collection survives restarts
    try:
        vectorstore.persist()
    except Exception:
        # some chroma installs persist automatically; ignore if not available
        pass

    return parent_id

# Build a retriever scoped to a specific company collection
def get_retriever_for_company(company_id: str, k: int = 5, fetch_k: int = 20):
    """
    Returns an MMR retriever that searches only the company's collection.
    """
    embeddings = get_embeddings()
    collection_name = f"company_{company_id}_chunks"

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_store"
    )

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k}
    )
    return retriever



# --------------------- TEAM VECTORSTORE ---------------------

# Add docs to team collection
def add_documents_to_team(company_id : str, team_id: str, documents, file_name: str = None):
    """
    - Splits docs into chunks
    - tags each chunk with metadata: team_id, parent_id, source
    - stores in Chroma collection: team_{team_id}_chunks
    """
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
    child_docs = child_splitter.split_documents(documents)

    parent_id = str(uuid.uuid4())
    for d in child_docs:
        d.metadata['company_id'] = str(company_id)
        d.metadata["team_id"] = str(team_id)
        d.metadata["parent_id"] = parent_id
        if file_name:
            d.metadata["source"] = file_name

    embeddings = get_embeddings()
    collection_name = f"team_{team_id}_{company_id}_chunks"


    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_store"
    )

    vectorstore.add_documents(child_docs)

    try:
        vectorstore.persist()
    except Exception:
        pass

    return parent_id

# Retriever for a team
def get_team_retriever(company_id : str, team_id: str, k: int = 5, fetch_k: int = 20):
    embeddings = get_embeddings()
    collection_name = f"team_{team_id}_{company_id}_chunks"

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_store"
    )

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k}
    )
    return retriever


# --------------------- PROJECT VECTORSTORE ---------------------
def add_documents_to_project(company_id: str, project_id: str, documents, file_name: str = None):
    # Split docs into chunks
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
    child_docs = child_splitter.split_documents(documents)

    parent_id = str(uuid.uuid4())
    for d in child_docs:
        d.metadata["company_id"] = str(company_id)
        d.metadata["project_id"] = str(project_id)
        d.metadata["parent_id"] = parent_id
        if file_name:
            d.metadata["source"] = file_name

    embeddings = get_embeddings()
    collection_name = f"project_{project_id}_company_{company_id}_chunks"

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_store"
    )

    vectorstore.add_documents(child_docs)
    vectorstore.persist()

    return parent_id


def get_project_retriever(company_id: str, project_id: str, k: int = 5, fetch_k: int = 20):

    embeddings = get_embeddings()
    collection_name = f"project_{project_id}_company_{company_id}_chunks"

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_store"
    )

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k}
    )
    return retriever
