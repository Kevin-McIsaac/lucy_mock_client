# Current State Architecture

The current state look like the diagram below. The green box are the major sub system, ie., 
- UI: The chat front end. Build in streamlit and run in streamlit.io. Uses async programming to process multiple, parallel streaming inputs. This improves the UX by lowering the latency (time to first character) 
- RAG Graph: This is a sate of the art multi-stage Graph based RAG. This also uses async programming to consume and creates multiple, parallel streaming inputs and outputs. 
- Policy Repository: A set of functons to find, strip, clean and chunk the Policy data. This is also based on streamlit.

The grey box are the commodity external (SaaS) sevices used by Policy Pal


```mermaid
graph LR
    %% INfrasuctures
    subgraph runtime[Streamlit & Python]
        UI
        RagGraph
        Repo
    end
    %% User Interface components
    subgraph "UI"
        UI_Chat["Broker Chat UI"]
        UI_Admin["Admin Portal UI"]
    end
    

    subgraph RagGraph["State of the Art <br> RAG Graph"]
        QueryProcess[Query]
        BankRAG["Individual Bank Policy RAG<br>(parallel asynchronous)"]
        Summarize["Summarize Results"]
    end


    subgraph External["External Services"]
        Auth["Authentication"]
        LLMs["LLM Providers"]
        Observability
        RDBMS["RDBMS<br>(Users, Q&A)"]
        VectorDB["Vector Database<br>(Policy Chunks)"]
    end

    subgraph Repo["Policy Repository"]
        PDF
        Markdown
        Cleaner[Cleaner <br> HTML, PDF, MD]
        Chunker[Chunker <br> Semantics & Context Aware ]
        WebScraper[Webscraper<br>HTML/Portal]

    end
    %% Main user flow
    UI_Chat -- Question --> QueryProcess
    QueryProcess --> BankRAG
    BankRAG -- "Answer per bank<br>Streaming/Asyncio" --> UI_Chat
    BankRAG <-- "Mulit-stage Retrival" --> VectorDB
    BankRAG <-- "Call LLM<br>Streaming/Asyncio" --> LLMs
    BankRAG --> Summarize --> RDBMS
    Summarize <-- "Call LLM" --> LLMs
    Summarize -- "Summary" --> UI_Chat
    QueryProcess["Query Expansion"]
    BankRAG --> Observability
    Summarize --> Observability

    %% Admin flow
    WebScraper
    UI_Admin -- "Sources" --> PDF -- "Policies" --> Cleaner
    UI_Admin -- "Sources" --> WebScraper -- "Policies" --> Cleaner 
    UI_Admin -- "Sources" --> Markdown -- "Policies" --> Cleaner
    Cleaner --> Chunker -- Semantics <br> Context--> VectorDB
    %% Authentication
    UI -- "Authenticate" --> Auth
	
    %%style
    style RagGraph fill:lightGreen
    style UI fill:lightGreen
    style Repo fill:lightGreen
    style External fill:lightGrey
    style runtime fill:lightGrey

    %% Set all edges and text to black
    linkStyle default stroke:#000000
    classDef default fill:#ffffff,stroke:#000000,color:#000000
```



## Future state
The LMG future state looks like the diagram below, where the green boxes are the code that can be migrated to Lucy AI. 
- RAG Graph: Would need to be decoupled via fastAPIs from the UI and connected to a myCRM / Lucy Chat UI. The external SaaS service would be replaced by LMG services. 
- Policy Repo:  The Policy Repo could be turned into a set of APIs that are called by myCRM but keeping this as a standalone streamlit ap, hosted in LMG, and connected to the LMG vector store would be a better option.

```mermaid
graph LR
    %% INfrasuctures

    subgraph environment[Lucy AI API - Uvicorn/ fastAPI]
        RagGraph
        Repo
    end
    %% User Interface components
    subgraph myCRM["My CRM <br> Widget & Proxy"]
        UI_Chat["Broker Chat UI"]
        UI_Admin["Admin Portal UI"]
    end
    

    subgraph RagGraph["State of the Art <br> RAG Graph"]
        QueryProcess[Query]
        BankRAG["Individual Bank Policy RAG<br>(parallel asynchronous)"]
        Summarize["Summarize Results"]
    end


    subgraph External["LMG Services"]
        Auth["Authentication"]
        LLMs["LLM Providers"]
        Observability
        RDBMS["RDBMS<br>(Users, Q&A)"]
        VectorDB["Vector Database<br>(Policy Chunks)"]
    end

    subgraph Repo["Policy Repository"]
        PDF
        Markdown
        Cleaner[Cleaner <br> HTML, PDF, MD]
        Chunker[Chunker <br> Semantics & Context Aware ]
        WebScraper[Webscraper<br>HTML/Portal]

    end
    %% Main user flow
    UI_Chat -- Question --> QueryProcess
    QueryProcess --> BankRAG
    BankRAG -- "Answer per bank<br>Streaming/Asyncio" --> UI_Chat
    BankRAG <-- "Mulit-stage Retrival" --> VectorDB
    BankRAG <-- "Call LLM<br>Streaming/Asyncio" --> LLMs
    BankRAG --> Summarize --> RDBMS
    Summarize <-- "Call LLM" --> LLMs
    Summarize -- "Summary" --> UI_Chat
    QueryProcess["Query Expansion"]
    BankRAG --> Observability
    Summarize --> Observability

    %% Admin flow
    WebScraper
    UI_Admin -- "Sources" --> PDF -- "Policies" --> Cleaner
    UI_Admin -- "Sources" --> WebScraper -- "Policies" --> Cleaner 
    UI_Admin -- "Sources" --> Markdown -- "Policies" --> Cleaner
    Cleaner --> Chunker -- Semantics <br> Context--> VectorDB
    %% Authentication
    myCRM -- "Authenticate" --> Auth
	
    %%style
    style RagGraph fill:lightGreen
    style Repo fill:lightGreen
  

    %% Set all edges and text to black
    linkStyle default stroke:#000000
    classDef default fill:#ffffff,stroke:#000000,color:#000000

```

## Roadmap
A road map needs to be prepared, and could be done many ways. My recommendation would be to do this in a incremental fashion, probably
1. Rehost the UI/RAG/Repo streamlit app in an LMG managed container. 
2. Migrate the  external services one by one
3. Partition the RAG from teh UI and run in streamlit
4. Migrate to a myCRM, JS client. 