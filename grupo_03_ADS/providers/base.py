from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class DatabaseProvider(ABC):
    
    @abstractmethod
    def fetch_all(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def fetch_one(self, query: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def execute(self, query: str, params: Dict[str, Any] = None) -> bool:
        pass