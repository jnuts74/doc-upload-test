import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import re
from utils.styles import get_css, apply_custom_styles
from utils.logger import logger

# Page config
st.set_page_config(
    page_title="System Logs",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom styles
apply_custom_styles()

# Top Navigation
st.markdown("""
<style>
    .top-nav {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2rem;
        padding: 1rem;
        background-color: #1E1E1E;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .nav-item {
        color: #FFFFFF;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: background-color 0.3s;
        font-weight: 500;
        cursor: pointer;
    }
    
    .nav-item:hover {
        background-color: #333333;
    }
    
    .nav-item.active {
        background-color: #4169e1;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
nav_items = {
    "🏠 Home": "Home",
    "🔍 Search": "pages/1_Document_Search",
    "📚 Library": "pages/2_Document_Library",
    "⚙️ Settings": "pages/5_Settings",
    "📋 Logs": ""
}

# Create navigation container
nav_container = st.container()
nav_cols = nav_container.columns(len(nav_items))

# Add navigation items
for idx, (label, page) in enumerate(nav_items.items()):
    with nav_cols[idx]:
        if st.button(
            label,
            key=f"nav_{page}",
            use_container_width=True,
            type="secondary" if page else "primary"
        ):
            if page:
                st.switch_page(page + ".py")

# Apply shared CSS
st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)

# Title
st.title("📋 Application Logs")

# Get project root directory
project_root = Path(__file__).parent.parent
logs_dir = project_root / "logs"

# Sidebar filters
st.sidebar.header("Log Filters")

# Date filter
today = datetime.now()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(today - timedelta(days=7), today),
    max_value=today
)

# Log level filter
log_levels = ["ALL", "INFO", "ERROR", "WARNING", "DEBUG"]
selected_level = st.sidebar.selectbox("Log Level", log_levels)

# Search filter
search_query = st.sidebar.text_input("Search in logs", "")

# Get log files
log_files = sorted(logs_dir.glob("app_*.log"), reverse=True)

if not log_files:
    st.warning("No log files found. Logs will appear here as the application runs.")
else:
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📊 Log Viewer", "📈 Statistics"])
    
    with tab1:
        # Log file selector
        selected_file = st.selectbox(
            "Select Log File",
            options=log_files,
            format_func=lambda x: x.stem.replace("app_", ""),
            index=0
        )
        
        # Read and filter logs
        if selected_file:
            with open(selected_file, 'r') as f:
                logs = f.readlines()
            
            # Apply filters
            filtered_logs = []
            for log in logs:
                # Parse log entry
                match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (\w+) - (.+)', log)
                if match:
                    timestamp, name, level, message = match.groups()
                    log_date = datetime.strptime(timestamp.split()[0], '%Y-%m-%d')
                    
                    # Apply date filter
                    if date_range[0] <= log_date.date() <= date_range[1]:
                        # Apply level filter
                        if selected_level == "ALL" or level == selected_level:
                            # Apply search filter
                            if not search_query or search_query.lower() in message.lower():
                                filtered_logs.append(log)
            
            # Display logs with syntax highlighting
            if filtered_logs:
                st.markdown("### Log Entries")
                for log in filtered_logs:
                    # Color-code based on log level
                    if "ERROR" in log:
                        st.markdown(f'<div style="color: #ff4444">{log}</div>', unsafe_allow_html=True)
                    elif "WARNING" in log:
                        st.markdown(f'<div style="color: #ffbb33">{log}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="color: #00C851">{log}</div>', unsafe_allow_html=True)
            else:
                st.info("No logs match the selected filters.")
    
    with tab2:
        # Basic statistics
        st.markdown("### Log Statistics")
        
        # Count by log level
        level_counts = {"INFO": 0, "ERROR": 0, "WARNING": 0, "DEBUG": 0}
        total_logs = 0
        
        for log_file in log_files:
            with open(log_file, 'r') as f:
                for line in f:
                    if " - doc_upload - " in line:
                        total_logs += 1
                        for level in level_counts:
                            if f" - {level} - " in line:
                                level_counts[level] += 1
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Logs", total_logs)
        with col2:
            st.metric("Info Logs", level_counts["INFO"])
        with col3:
            st.metric("Warning Logs", level_counts["WARNING"])
        with col4:
            st.metric("Error Logs", level_counts["ERROR"])
        
        # Log file information
        st.markdown("### Log Files")
        for log_file in log_files:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                error_count = sum(1 for line in lines if " - ERROR - " in line)
                warning_count = sum(1 for line in lines if " - WARNING - " in line)
                info_count = sum(1 for line in lines if " - INFO - " in line)
                
                st.markdown(f"""
                **{log_file.stem.replace('app_', '')}**
                - Total entries: {len(lines)}
                - Errors: {error_count}
                - Warnings: {warning_count}
                - Info: {info_count}
                """)

# Add refresh button
if st.button("🔄 Refresh Logs"):
    st.experimental_rerun() 