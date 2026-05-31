# 🔎 BugSense — AI Bug Analyst

BugSense is an intelligent, conversational code analysis tool built to help developers and students not just fix their code, but understand **why it broke**.

Powered by the **Google Gemini API**, BugSense acts as a virtual senior software engineer—identifying logic flaws, explaining root causes step-by-step, and providing visual code diffs for easy resolution.

---

## ✨ Key Features

### 🧠 Deep Context Analysis
Analyze:

- Single code snippets
- Entire multi-file project directories
- Raw source code fetched directly from a GitHub URL

### 🚦 Visual Diff Viewer
Instantly see exactly what changed with a built-in **Red/Green code diff viewer**, making additions and deletions easy to identify.

### 💬 Conversational Debugging
Need clarification? BugSense maintains conversation context, allowing you to ask follow-up questions and continue debugging naturally.

### 🗄️ Persistent Local History
All debugging sessions and chat histories are automatically saved using **SQLite**. Reload previous sessions anytime from the sidebar.

### 🛡️ Smart "No-Bug" Detection
Recognizes structurally sound code and explains why it is correct instead of inventing non-existent issues.

---

## 🛠️ Tech Stack

| Component | Technology |
|------------|------------|
| Frontend | Streamlit (Python) |
| AI Engine | Google Gemini API (`gemini-3-flash-preview`) |
| Database | SQLite3 |
| Utilities | requests, difflib |

---

## 🚀 Installation & Setup

Follow these steps to run BugSense locally.

### 1. Clone the Repository

```bash
git clone https://github.com/Ayeza-Irfan/BugSenseAI.git
cd BugSenseAI
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install streamlit google-genai python-dotenv requests pillow
```

### 4. Set Up Your API Key

BugSense requires a Google Gemini API key.

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Run the Application

```bash
streamlit run streamlit_app.py
```

> **Note:** The SQLite database (`bugsense_history.db`) will be generated automatically when the application is launched for the first time.

---

## 📂 Project Structure

```plaintext
bugsense-ai/
├── streamlit_app.py      # Main Streamlit UI and application logic
├── agent.py              # Gemini API calls and chat session management
├── database.py           # SQLite persistence layer
├── input_parser.py       # Language detection and multi-file processing
├── prompt_engine.py      # Prompt construction and AI instructions
├── output_formatter.py   # Structured output parsing and markdown cleanup
├── .env                  # Stores GEMINI_API_KEY (not tracked)
├── logo.png              # Application branding asset
└── README.md             # Project documentation
```

---

## 💡 How to Use

### 1. Input Code
Choose one of the following methods:

- Paste a code snippet
- Upload a folder containing `.py`, `.java`, or `.cpp` files
- Import a raw source file from GitHub

### 2. Analyze
Click **Analyze** and wait for the AI to generate:

- Bug Type
- Root Cause
- Corrected Code

### 3. Review
Inspect the **Visual Diff Viewer** to understand exactly what was changed.

### 4. Chat
Use the built-in chat interface to ask follow-up questions about the bug, logic, or proposed solution.

### 5. Resume
Open the sidebar to access previous debugging sessions and instantly restore context and conversation history.

---

## 🎯 Example Workflow

```text
Code Input
    ↓
AI Analysis
    ↓
Root Cause Detection
    ↓
Corrected Code Generation
    ↓
Visual Diff Comparison
    ↓
Follow-Up Discussion
```

---

## 🖼️ Supported Input Methods

✅ Direct code snippets

✅ Multi-file project uploads

✅ GitHub raw file imports

✅ Persistent debugging sessions

---

## 👨‍💻 Author

Developed as a **Final Year Artificial Intelligence Semester Project**.

---

## 📜 License

This project is intended for educational and research purposes.

Feel free to modify and extend it for your own learning and development projects.
