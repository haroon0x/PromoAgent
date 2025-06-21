# PromoAgent

PromoAgent is an autonomous Reddit marketing agent designed to help brands and products engage with relevant Reddit threads in a natural, non-spammy way. It automatically searches for discussions, generates context-aware replies, and can post them directly or provide previews for review.

## Features
- **Autonomous Reddit Engagement:** Finds and replies to relevant Reddit threads based on your topic and brand instructions.
- **Customizable Brand Voice:** Choose from preset or custom brand voices for authentic, on-brand replies.
- **Real-time Activity Feed:** Monitor agent actions and results live from a modern frontend UI.
- **Preview or Auto-Post:** Run in preview mode or let the agent post replies automatically.

## Tech Stack
- **Frontend:** React + Tailwind CSS (Vite)
- **Backend:** FastAPI (Python)
- **AI Model:** Uses [Alchemyst AI](https://getalchemyst.ai/) (alchemyst-ai/alchemyst-c1) via LangChain for reply generation
- **Reddit API:** For searching threads and posting comments
- **Optional:** Supabase for duplicate tracking (prepared, not active by default)

## Architecture Overview
- The frontend sends agent requests to the FastAPI backend.
- The backend orchestrates the agent pipeline using LangChain and Alchemyst AI for generating replies.
- Results and activity logs are streamed back to the frontend for real-time updates.

---

```graph TD
    A["Frontend UI<br/>(Input & Config)"] -->|1. Start Agent| B["Backend API<br/>(FastAPI Server)"];
    B -->|2. Run Pipeline| C["Agent Graph<br/>(LangGraph)"];

    subgraph "Agent Actions"
        C --> D["Search Threads"];
        D --> E["Generate Reply"];
        E --> F["Post Reply"];
    end

    D -->|Reddit API| G["<br/>Reddit<br/>"];
    E -->|LLM API| H["<br/>Alchemyst AI<br/>"];
    F -->|Reddit API| G;

    C -->|3. Stream Status| B;
    B -->|4. Poll for Updates| A;
    A --> I["Activity Feed<br/>(Real-time Log)"];
    A --> J["Results Section<br/>(Comment URL)"];

    style A fill:#D6EAF8,stroke:#3498DB
    style I fill:#D5F5E3,stroke:#2ECC71
    style J fill:#D5F5E3,stroke:#2ECC71
```


*PromoAgent is designed for responsible, authentic engagement. Please use in accordance with Reddit's rules and best practices.*