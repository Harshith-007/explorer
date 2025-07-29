# System Design Document - Python FastAPI Implementation

## Architecture Overview

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │ External Auth   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│ (Google/MS)     │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  File Storage   │
                       │  (Local FS)     │
                       └─────────────────┘