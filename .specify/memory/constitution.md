<!--
Version change: 0.1.0 (assumed initial) -> 0.2.0
Modified principles:
  - [PRINCIPLE_1_NAME] -> Technical Accuracy
  - [PRINCIPLE_2_NAME] -> Clear Teaching
  - [PRINCIPLE_3_NAME] -> Source-Verifiable Claims
  - [PRINCIPLE_4_NAME] -> Consistent Modular Structure
  - [PRINCIPLE_5_NAME] -> Grounded Chatbot Responses
Added sections:
  - Key Standards
  - Constraints
  - Success Criteria
Removed sections:
  - None
Templates requiring updates:
  - .specify/templates/plan-template.md (⚠ pending)
  - .specify/templates/spec-template.md (⚠ pending)
  - .specify/templates/tasks-template.md (⚠ pending)
  - .specify/templates/commands/*.md (⚠ pending)
Follow-up TODOs:
  - TODO(RATIFICATION_DATE): Original adoption date
-->
# AI/Robotics Book + Embedded RAG Chatbot Constitution

## Core Principles

### I. Technical Accuracy
ROS 2, Gazebo, Unity, Isaac Sim, VLA concepts must be correct and citable.

### II. Clear Teaching
Content must be clear and accessible for undergraduate robotics learners (Flesch-Kincaid ~10–14).

### III. Source-Verifiable Claims
All claims and facts presented in the book must be traceable to a reliable source.

<h3>IV. Consistent Modular Structure</h3>
Follow Docusaurus + Spec-Kit Plus conventions for consistent organization and modularity.

<h3>V. Grounded Chatbot Responses</h3>
Chatbot responses MUST only be derived from the book text; no external knowledge or generated content.

## Key Standards

- Follow Docusaurus + Spec-Kit Plus conventions.
- All robotics concepts must be correct and citable.
- Code samples must be runnable (Python/ROS 2/FastAPI).
- Chatbot must restrict answers to retrieved context.

## Constraints

- 10–14 chapters covering ROS2, Gazebo/Unity, Isaac, VLA, Capstone.
- Include diagrams, URDF, sensor models, workflows.
- Deploy book on GitHub Pages; deploy RAG backend publicly.
- Writing level: undergraduate robotics (Flesch-Kincaid ~10–14).

## Success Criteria

- Book fully published and reproducible.
- RAG chatbot returns only grounded responses from book text.

## Governance

This constitution supersedes all other practices. Amendments require documentation, approval, and a migration plan. All PRs/reviews must verify compliance. Complexity must be justified. Use relevant guidance files for runtime development guidance.

**Version**: 0.2.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2025-12-07
