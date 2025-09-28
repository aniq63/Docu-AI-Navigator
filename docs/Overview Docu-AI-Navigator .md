# Tutorial: Docu-AI-Navigator

Docu-AI-Navigator is an **AI-driven platform** that helps companies, teams, and projects *securely manage and interact with their documents*. It allows users to **upload PDFs**, which are then processed by AI to enable intelligent features like *asking questions and getting factual answers* (RAG) and *generating detailed project plans* based on their stored information.


## Visual Overview

```mermaid
flowchart TD
    A0["Hierarchical Data Management
"]
    A1["API Endpoints & Routing
"]
    A2["Data Modeling & Validation
"]
    A3["Retrieval-Augmented Generation (RAG)
"]
    A4["Document Ingestion & Processing
"]
    A5["Large Language Model (LLM) Integration
"]
    A6["Frontend User Interface
"]
    A0 -- "Defines structure via" --> A2
    A6 -- "Interacts via" --> A1
    A1 -- "Manages entities within" --> A0
    A1 -- "Validates inputs with" --> A2
    A1 -- "Triggers" --> A4
    A4 -- "Prepares data for" --> A3
    A3 -- "Leverages" --> A5
    A5 -- "Extracts info during" --> A4
    A0 -- "Scopes storage in" --> A4
    A1 -- "Invokes specialized tasks" --> A5
```

## Chapters

1. [Frontend User Interface
](01_frontend_user_interface_.md)
2. [API Endpoints & Routing
](02_api_endpoints___routing_.md)
3. [Data Modeling & Validation
](03_data_modeling___validation_.md)
4. [Hierarchical Data Management
](04_hierarchical_data_management_.md)
5. [Large Language Model (LLM) Integration
](05_large_language_model__llm__integration_.md)
6. [Document Ingestion & Processing
](06_document_ingestion___processing_.md)
7. [Retrieval-Augmented Generation (RAG)
](07_retrieval_augmented_generation__rag__.md)
