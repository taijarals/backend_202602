"""
Streamlit Session State Management.
"""
import streamlit as st
from typing import Optional, Dict, Any
from dataclasses import dataclass
import requests
import os

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")


@dataclass
class User:
    """User session data."""
    id: str
    nome: str
    email: str
    role: str
    pontuacao_total: int = 0
    nivel: int = 1
    avatar_url: Optional[str] = None


class SessionManager:
    """Manage user session state."""

    @staticmethod
    def init_session():
        """Initialize session state variables."""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user" not in st.session_state:
            st.session_state.user = None
        if "token" not in st.session_state:
            st.session_state.token = None
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Dashboard"

    @staticmethod
    def login(user_data: Dict[str, Any], token: str):
        """Set user as logged in."""
        st.session_state.authenticated = True
        st.session_state.token = token
        st.session_state.user = User(
            id=str(user_data.get('id', '')),
            nome=user_data.get('nome', ''),
            email=user_data.get('email', ''),
            role=user_data.get('role', 'student'),
            pontuacao_total=user_data.get('pontuacao_total', 0),
            nivel=user_data.get('nivel', 1),
            avatar_url=user_data.get('avatar_url')
        )

    @staticmethod
    def logout():
        """Clear session state."""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.token = None

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated."""
        return st.session_state.get("authenticated", False)

    @staticmethod
    def get_user() -> Optional[User]:
        """Get current user."""
        return st.session_state.get("user")

    @staticmethod
    def get_token() -> Optional[str]:
        """Get auth token."""
        return st.session_state.get("token")

    @staticmethod
    def update_user(data: Dict[str, Any]):
        """Update user data."""
        if st.session_state.user:
            for key, value in data.items():
                if hasattr(st.session_state.user, key):
                    setattr(st.session_state.user, key, value)

    @staticmethod
    def set_page(page: str):
        """Set current page."""
        st.session_state.current_page = page

    @staticmethod
    def get_page() -> str:
        """Get current page."""
        return st.session_state.get("current_page", "Dashboard")


class APIClient:
    """API client for backend communication."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token."""
        headers = {"Content-Type": "application/json"}
        token = SessionManager.get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """GET request."""
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self._get_headers(),
            params=params
        )
        return self._handle_response(response)

    def post(self, endpoint: str, data: Dict) -> Dict:
        """POST request."""
        response = requests.post(
            f"{self.base_url}{endpoint}",
            headers=self._get_headers(),
            json=data
        )
        return self._handle_response(response)

    def put(self, endpoint: str, data: Dict) -> Dict:
        """PUT request."""
        response = requests.put(
            f"{self.base_url}{endpoint}",
            headers=self._get_headers(),
            json=data
        )
        return self._handle_response(response)

    def delete(self, endpoint: str) -> Dict:
        """DELETE request."""
        response = requests.delete(
            f"{self.base_url}{endpoint}",
            headers=self._get_headers()
        )
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Dict:
        """Handle API response."""
        try:
            if response.status_code == 204:
                return {"success": True}
            return response.json()
        except Exception:
            return {"error": True, "message": response.text}


# Global API client
api = APIClient()
