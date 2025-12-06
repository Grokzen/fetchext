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
