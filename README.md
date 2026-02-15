# 🛠️ WIT - Basic Version Control System

**WIT** is a robust, lightweight version control tool inspired by Git. Developed in Python, it allows users to manage project snapshots, track file changes, and navigate through the development history via a Command-Line Interface (CLI).

---

## 🏗️ Architecture & Design Principles

This project adheres to **Professional Software Engineering** standards:

* **Layered Architecture**: Complete separation between the CLI Presentation Layer (`main.py`) and the Core Business Logic (`wit_engine.py`).
* **Modularity**: Reusable utility functions isolated in `utils.py` for cleaner code maintenance.
* **State Management**: System state and metadata are persisted using JSON serialization in a hidden `.wit` directory.
* **Clean Code**: Built following **PEP8** guidelines with descriptive naming and clear logical flow.

---

## 📂 Project Structure

```text
WIT-Project---Ayala-Lali/    # Root Directory
├── README.md                # Main documentation (The file you are reading)
├── .gitignore               # Ensures metadata/cache stays local
└── witProject/              # Source Code Directory
    ├── main.py              # CLI Entry point
    ├── wit_engine.py        # Core logic
    ├── utils.py             # Helpers
    └── requirements.txt     # Dependencies
