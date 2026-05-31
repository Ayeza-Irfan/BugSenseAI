import streamlit as st
import streamlit.components.v1 as components
import requests
import difflib
import uuid
import database as db 
from PIL import Image  

from agent import BugSenseAgent
from input_parser import InputParser
from prompt_engine import PromptEngine
from output_formatter import OutputFormatter

# 1. Load the image file
# logo = Image.open("logo.png") 

# 2. Set it as the browser tab icon (favicon)
st.set_page_config(page_title="BugSense AI", page_icon="🔎", layout="wide")

# 3. Create a custom header layout using columns
# col1, col2 = st.columns([1, 15]) 

# with col1:
#     st.image(logo, width=60) 

# with col2:
st.title(" 🔎 BugSense — AI Bug Analyst")

# Initialize Logic & Database
db.init_db()  
parser = InputParser()
engine = PromptEngine()
agent = BugSenseAgent()
formatter = OutputFormatter()

# --- INITIALIZE SESSION STATE ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "original_code" not in st.session_state:
    st.session_state.original_code = ""
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "cached_analysis" not in st.session_state:
    st.session_state.cached_analysis = {}

# --- SIDEBAR: HISTORY MENU ---
with st.sidebar:
    st.header("🗄️ Analysis History")
    past_sessions = db.get_all_sessions()
    
    if st.button("➕ Start New Analysis", use_container_width=True):
        st.session_state.current_session_id = None
        st.session_state.analysis_complete = False
        st.session_state.chat_history = []
        st.session_state.cached_analysis = {}
        st.session_state.chat_session = None
        st.rerun()
        
    st.divider()
    
    for session in past_sessions:
        # CLEANUP TITLE: Get bug type, truncate if it's too long, fallback to "Analysis"
        bug_label = session.get('bug_type', '')
        if not bug_label or bug_label.strip() in ["", "Unknown"]:
            bug_label = "Analysis"
        if len(bug_label) > 22:
            bug_label = bug_label[:19] + "..."
            
        # Format: 📝 ValueError (2026-05-31)
        short_date = session['timestamp'].split()[0]
        btn_label = f"📝 {bug_label} ({short_date})"
        
        if st.button(btn_label, key=session['session_id'], use_container_width=True):
            loaded_data = db.load_session(session['session_id'])
            
            st.session_state.current_session_id = loaded_data['session_id']
            st.session_state.original_code = loaded_data['original_code']
            st.session_state.chat_history = loaded_data['chat_history']
            st.session_state.cached_analysis = {
                "Bug Type": loaded_data['bug_type'],
                "Root Cause": loaded_data['root_cause'],
                "Corrected Code": loaded_data['corrected_code']
            }
            # We purposely set this to None. agent.py will dynamically rebuild it if they chat!
            st.session_state.chat_session = None 
            st.session_state.analysis_complete = True
            st.rerun()

# --- HELPER FUNCTIONS ---
def fetch_github_file(url: str) -> str:
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        response = requests.get(raw_url)
        if response.status_code == 200:
            return response.text, url.split("/")[-1]
        else:
            return None, f"Failed to fetch file. Status Code: {response.status_code}"
    except Exception as e:
        return None, str(e)

def render_diff(original: str, corrected_markdown: str):
    clean_corrected = formatter.clean_code_block(corrected_markdown)
    d = difflib.HtmlDiff()
    diff_html = d.make_file(original.splitlines(), clean_corrected.splitlines(), 
                            fromdesc="Original Code", todesc="Corrected Code")
    styled_html = f"""
    <style>
        table.diff {{font-family: monospace; width: 100%; border-collapse: collapse;}}
        .diff_header {{background-color: #e0e0e0;}}
        td.diff_header {{text-align:right; padding: 0 5px;}}
        .diff_next {{display: none;}}
        .diff_add {{background-color: #c6efce;}}
        .diff_chg {{background-color: #ffeb9c;}}
        .diff_sub {{background-color: #ffc7ce;}}
    </style>
    {diff_html}
    """
    components.html(styled_html, height=400, scrolling=True)

def run_analysis(parsed_input: dict):
    st.session_state.original_code = parsed_input["code"]
    st.session_state.chat_history = [] 
    st.session_state.analysis_complete = False 
    
    with st.spinner("Analyzing code..."):
        prompt = engine.build(parsed_input)
        response_text, active_chat = agent.start_chat_and_run(prompt)
        
        st.session_state.chat_session = active_chat
        parsed_sections = formatter.parse_sections(response_text)
        
        if not parsed_sections:
            parsed_sections = {"Bug Type": "Unknown", "Root Cause": response_text, "Corrected Code": "None"}
            
        st.session_state.cached_analysis = parsed_sections
        st.session_state.current_session_id = str(uuid.uuid4())
        
        db.save_session(
            session_id=st.session_state.current_session_id,
            original_code=st.session_state.original_code,
            bug_type=parsed_sections.get('Bug Type', ''),
            root_cause=parsed_sections.get('Root Cause', ''),
            corrected_code=parsed_sections.get('Corrected Code', ''),
            chat_history=st.session_state.chat_history
        )

        st.session_state.analysis_complete = True

def display_cached_analysis():
    parsed_sections = st.session_state.cached_analysis
    if not parsed_sections:
        return
        
    # NEW: Display original code in an expander so the user has context
    st.markdown("### 📄 Original Code Context")
    with st.expander("View Source Code", expanded=False):
        st.code(st.session_state.original_code)

    st.divider()
    
    bug_type = parsed_sections.get('Bug Type', 'Unknown').strip()
    is_correct = bug_type.lower() in ["none", "no bug found", "no bug"]

    if is_correct:
        st.success("✅ **No Bugs Found!**")
        st.info(f"**Analysis:**\n\n{parsed_sections.get('Root Cause', 'The code is structurally and logically sound.')}")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.error(f"🚨 **Bug Type**\n\n{bug_type}")
        with col2:
            st.warning("🔍 **Root Cause Analysis**")
            st.write(parsed_sections.get('Root Cause', 'No explanation provided.'))

        st.success("✅ **Resolution**")
        
        if "Corrected Code" in parsed_sections and parsed_sections["Corrected Code"].strip().lower() != "none":
            code_tab, diff_tab = st.tabs(["Corrected Code", "Visual Diff Viewer"])
            with code_tab:
                st.markdown(parsed_sections['Corrected Code'])
            with diff_tab:
                st.info("Highlighted lines that were added (Green), removed (Red), or changed (Yellow).")
                render_diff(st.session_state.original_code, parsed_sections['Corrected Code'])

# --- MAIN INPUT TABS ---
if not st.session_state.analysis_complete:
    tab1, tab2, tab3 = st.tabs(["🚀 Paste Code", "📁 Upload Project", "🔗 Import GitHub"])

    with tab1:
        st.subheader("Paste your code snippet")
        raw_code = st.text_area("Paste code here:", height=300, placeholder="def my_function():...")
        error_msg = st.text_input("Error message (optional):", key="err_paste")
        
        if st.button("Analyze Snippet"):
            if raw_code.strip():
                parsed = parser.parse_single(raw_code, error_msg)
                run_analysis(parsed)
            else:
                st.warning("Please paste some code first!")

    with tab2:
        st.subheader("Upload files or a directory")
        upload_mode = st.toggle("Folder Upload Mode")
        uploaded_files = st.file_uploader(
            "Select Files", 
            accept_multiple_files="directory" if upload_mode else True,
            type=["py", "java", "c", "cpp"]
        )
        error_msg_upload = st.text_input("Error message for project (optional):", key="err_upload")

        if uploaded_files:
            if st.button("Analyze Entire Project"):
                files_data = [{"filename": f.name, "code": f.getvalue().decode("utf-8")} for f in uploaded_files]
                parsed = parser.parse_multiple(files_data, error_msg_upload)
                run_analysis(parsed)

    with tab3:
        st.subheader("Import a single file from GitHub")
        github_url = st.text_input("GitHub File URL:", placeholder="https://github.com/user/repo/blob/main/script.py")
        error_msg_gh = st.text_input("Error message (optional):", key="err_gh")
        
        if st.button("Fetch and Analyze"):
            if github_url.strip():
                with st.spinner("Fetching code from GitHub..."):
                    code_text, filename = fetch_github_file(github_url)
                    if code_text:
                        st.success(f"Successfully fetched `{filename}`!")
                        parsed = parser.parse_single(code_text, error_msg_gh, filename=filename)
                        run_analysis(parsed)
                    else:
                        st.error(f"Error fetching file: {filename}")
            else:
                st.warning("Please enter a GitHub URL.")

# --- RESULTS & CONVERSATIONAL DEBUGGING ---
if st.session_state.analysis_complete:
    display_cached_analysis()
    
    st.divider()
    st.subheader("💬 Ask Follow-up Questions")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # REMOVED the restrictive session check. Now users can always type!
    if user_question := st.chat_input("Ask your queries here..."):
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Pass the context into the updated agent method
                response_text, active_session = agent.send_followup(
                    chat_session=st.session_state.chat_session, 
                    message=user_question,
                    context_code=st.session_state.original_code,
                    chat_history=st.session_state.chat_history
                )
                
                # Update our session state so future messages don't have to rebuild it
                st.session_state.chat_session = active_session
                
                st.markdown(response_text)
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
        # Save the updated history back to SQLite immediately
        db.save_session(
            session_id=st.session_state.current_session_id,
            original_code=st.session_state.original_code,
            bug_type=st.session_state.cached_analysis.get('Bug Type', ''),
            root_cause=st.session_state.cached_analysis.get('Root Cause', ''),
            corrected_code=st.session_state.cached_analysis.get('Corrected Code', ''),
            chat_history=st.session_state.chat_history
        )
        st.rerun()