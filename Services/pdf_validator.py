from langchain_community.document_loaders import PyPDFLoader

def document_validator(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    if not documents:
        raise ValueError("No documents were loaded. Check the file path or PDF content.")
    return documents