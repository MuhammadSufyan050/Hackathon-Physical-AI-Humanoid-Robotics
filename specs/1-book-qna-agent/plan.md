# Implementation Plan: Book Q&A Retrieval Agent

**Branch**: `1-book-qna-agent` | **Date**: 2025-12-23 | **Spec**: [link](../specs/1-book-qna-agent/spec.md)

**Input**: Feature specification from `/specs/1-book-qna-agent/spec.md`

## Summary

Implementation of a retrieval-enabled agent for book Q&A using OpenAI Agents SDK with Qdrant vector database integration. The agent will accept user questions via CLI, generate Cohere embeddings for semantic search, retrieve relevant content from Qdrant, and generate grounded answers with source references.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: OpenAI Agents SDK, Cohere API, Qdrant client, Pydantic, python-dotenv
**Storage**: N/A (using external Qdrant Cloud service)
**Testing**: pytest for unit and integration tests
**Target Platform**: Linux/Mac/Windows CLI environment
**Project Type**: Single CLI application
**Performance Goals**: Response time under 10 seconds for 90% of queries
**Constraints**: Must use only retrieved content for answers, include source metadata, handle out-of-scope questions gracefully
**Scale/Scope**: Single user CLI interaction, supporting book content Q&A

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Grounded Chatbot Responses**: The agent must only generate responses based on retrieved content from the book, not from external knowledge or generated content. This aligns with principle V in the constitution.
2. **Technical Accuracy**: Implementation must correctly use OpenAI Agents SDK, Cohere embeddings, and Qdrant vector database as specified.
3. **Consistent Modular Structure**: Follow Docusaurus + Spec-Kit Plus conventions for project organization.

All constitution requirements are satisfied by the feature specification.

## Project Structure

### Documentation (this feature)

```text
specs/1-book-qna-agent/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── agents/
│   ├── __init__.py
│   ├── book_qna_agent.py      # Main agent implementation
│   └── tools/
│       ├── __init__.py
│       └── retrieval_tool.py  # Qdrant retrieval tool
├── models/
│   ├── __init__.py
│   ├── query.py              # Query and response models
│   └── document.py           # Document and metadata models
├── services/
│   ├── __init__.py
│   ├── embedding_service.py  # Cohere embedding generation
│   └── qdrant_service.py     # Qdrant client wrapper
├── cli/
│   ├── __init__.py
│   └── main.py              # CLI entry point
└── config/
    ├── __init__.py
    └── settings.py           # Configuration and settings
```

tests/
├── unit/
│   ├── agents/
│   ├── models/
│   └── services/
├── integration/
│   └── qdrant_integration_test.py
└── contract/
    └── tool_contract_test.py

.env.example
requirements.txt
README.md

**Structure Decision**: Single CLI project structure chosen to match the requirement of a local CLI or script-based interaction without web server components.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |