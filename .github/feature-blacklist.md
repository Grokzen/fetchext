# Feature Blacklist

This file contains a list of features that have been explicitly rejected for the `fetchext` project.
These features should **NOT** be implemented, suggested, or added to the roadmap.

## 🚫 Rejected Features

### 1. Cloud Storage Integration (S3, Azure Blob, GCS)
- **Reason**: `fetchext` is designed as a local-first CLI tool. It should operate on the local filesystem. Adding cloud storage dependencies (boto3, etc.) bloats the project and complicates the scope. Users can pipe output to other tools (e.g., `aws s3 cp`) if they need cloud upload.
- **Status**: Permanently Rejected.

### 2. GUI (Graphical User Interface)
- **Reason**: The project is strictly a CLI tool. A TUI (Terminal User Interface) is acceptable (e.g., `textual`), but a full windowed GUI (Qt, Tkinter) is out of scope.
- **Status**: Permanently Rejected.

### 3. Web Dashboard / Web Server
- **Reason**: Hosting a web server (Flask/Django/FastAPI) for a dashboard violates the "stateless CLI" philosophy. The tool should be usable in scripts and pipelines, not require a running daemon or browser interaction for management.
- **Status**: Permanently Rejected.

### 4. AI / LLM Integration
- **Reason**: The project focuses on deterministic, reproducible analysis. AI/LLM integration introduces external dependencies, privacy concerns, and non-deterministic behavior that is out of scope for this tool.
- **Status**: Permanently Rejected.

### 5. Static Type Checking / Type Hints
- **Reason**: The codebase is designed to be dynamic and clean Python. Type hints (e.g., `def foo(x: int) -> str:`) add visual noise and rigidity that is not desired for this specific project.
- **Status**: Permanently Rejected.
