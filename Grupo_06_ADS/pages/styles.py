"""
Streamlit Styling and Theme Configuration.

Dark theme with modern SaaS-like design.
"""

# Dark Theme CSS Styles
DARK_THEME_CSS = """
<style>
    /* Global Styles */
    .stApp {
        background-color: #0f1419 !important;
        color: #e7e9ea !important;
    }

    /* Main Content */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #16202a !important;
        border-right: 1px solid #2f3336;
    }

    section[data-testid="stSidebar"] .sidebar-content {
        background-color: #16202a !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Cards */
    .card {
        background: linear-gradient(135deg, #1a1f2e 0%, #16202a 100%);
        border: 1px solid #2f3336;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }

    .card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1f2e 0%, #16202a 100%);
        border: 1px solid #2f3336;
        border-radius: 12px;
        padding: 1rem;
    }

    [data-testid="stMetricLabel"] {
        color: #8b98a5 !important;
        font-size: 0.875rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
    }

    .stButton button[kind="secondary"] {
        background: transparent;
        border: 1px solid #3b82f6;
        color: #3b82f6;
    }

    .stButton button[kind="secondary"]:hover {
        background: rgba(59, 130, 246, 0.1);
    }

    /* Text Inputs */
    .stTextInput input, .stTextArea textarea {
        background-color: #1a1f2e !important;
        border: 1px solid #2f3336 !important;
        border-radius: 8px !important;
        color: #e7e9ea !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }

    .stTextInput label, .stTextArea label {
        color: #8b98a5 !important;
    }

    /* Select Box */
    .stSelectbox {
        background-color: #1a1f2e !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1a1f2e !important;
        border: 1px solid #2f3336 !important;
        border-radius: 8px !important;
    }

    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: #3b82f6 !important;
    }

    /* DataFrames */
    .stDataFrame {
        background: transparent;
        border: 1px solid #2f3336;
        border-radius: 12px;
        overflow: hidden;
    }

    .stDataFrame table {
        background-color: #1a1f2e !important;
    }

    .stDataFrame th {
        background-color: #16202a !important;
        color: #8b98a5 !important;
        border-bottom: 1px solid #2f3336 !important;
    }

    .stDataFrame td {
        color: #e7e9ea !important;
        border-bottom: 1px solid #2f333622 !important;
    }

    .stDataFrame tr:hover td {
        background-color: #16202a !important;
    }

    /* Expander */
    .stExpander {
        background: linear-gradient(135deg, #1a1f2e 0%, #16202a 100%);
        border: 1px solid #2f3336;
        border-radius: 12px;
    }

    .stExpander header {
        color: #e7e9ea !important;
    }

    /* Progress Bar */
    .stProgressBar > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.25rem;
    }

    .badge-success {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-warning {
        background-color: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .badge-error {
        background-color: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .badge-info {
        background-color: rgba(59, 130, 246, 0.2);
        color: #3b82f6;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* Custom Divs */
    .metric-highlight {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    .error-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid #2f3336;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #8b98a5;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
    }

    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #3b82f6 !important;
        border-bottom: 2px solid #3b82f6 !important;
    }

    /* Alerts */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 8px;
        padding: 1rem;
    }

    /* Spinner */
    .stSpinner > div {
        border-color: #3b82f6 transparent transparent transparent !important;
    }

    /* Avatar */
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 1.2rem;
    }

    /* Leaderboard */
    .leaderboard-item {
        display: flex;
        align-items: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1a1f2e 0%, #16202a 100%);
        border: 1px solid #2f3336;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }

    .leaderboard-item:hover {
        border-color: #3b82f6;
        transform: translateX(4px);
    }

    .leaderboard-rank {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.1rem;
        margin-right: 1rem;
    }

    .rank-1 {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: #1a1f2e;
    }

    .rank-2 {
        background: linear-gradient(135deg, #9ca3af, #6b7280);
        color: #1a1f2e;
    }

    .rank-3 {
        background: linear-gradient(135deg, #cd7f32, #b45309);
        color: white;
    }

    .rank-default {
        background: #2f3336;
        color: #8b98a5;
    }

    /* Medal Icons */
    .medal {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #16202a;
    }

    ::-webkit-scrollbar-thumb {
        background: #3b82f6;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #2563eb;
    }

    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }

    /* Color System */
    :root {
        --bg-primary: #0f1419;
        --bg-secondary: #16202a;
        --bg-tertiary: #1a1f2e;
        --border-color: #2f3336;
        --text-primary: #ffffff;
        --text-secondary: #e7e9ea;
        --text-muted: #8b98a5;
        --accent-primary: #3b82f6;
        --accent-secondary: #2563eb;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --purple: #8b5cf6;
        --cyan: #06b6d4;
        --pink: #ec4899;
    }
</style>
"""

def apply_dark_theme():
    """Apply dark theme to Streamlit app."""
    import streamlit as st
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)


# Icon mappings for different entities
ICONS = {
    "trophy": "T",
    "star": "S",
    "medal": "M",
    "award": "A",
    "zap": "Z",
    "compass": "C",
    "users": "U",
    "lightbulb": "L",
    "crown": "R",
    "fire": "F",
    "target": "G",
    "book": "B",
    "check": "-",
    "x": "X",
}

# Color palette for charts and elements
COLORS = {
    "primary": "#3B82F6",
    "secondary": "#2563EB",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "purple": "#8B5CF6",
    "cyan": "#06B6D4",
    "pink": "#EC4899",
    "orange": "#F97316",
    "teal": "#14B8A6",
}

DIFFICULTY_COLORS = {
    "facil": "#10B981",
    "media": "#F59E0B",
    "dificil": "#EF4444",
    "expert": "#8B5CF6",
}

STATUS_COLORS = {
    "pendente": "#F59E0B",
    "em_progresso": "#3B82F6",
    "completa": "#10B981",
    "rejeitada": "#EF4444",
    "nota_atribuida": "#06B6D4",
}
