"""Hash providers for file processing."""

from abc import ABC, abstractmethod
import hashlib
import os
from typing import Union

class HashProvider(ABC):
    """Abstract base class for hash providers."""
    
    @abstractmethod
    def calculate_hash(self, content: Union[str, bytes]) -> str:
        """Calculate hash for file content."""
        pass

class SHA256HashProvider(HashProvider):
    """Production hash provider using SHA256."""
    
    def calculate_hash(self, content: Union[str, bytes]) -> str:
        """Calculate SHA256 hash of content."""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        return hashlib.sha256(content).hexdigest()

class MockHashProvider(HashProvider):
    """Mock hash provider for development."""
    
    def __init__(self):
        self.hash_counter = 0
    
    def calculate_hash(self, content: Union[str, bytes]) -> str:
        """Generate predictable mock hash for development."""
        self.hash_counter += 1
        # Create a predictable but unique hash for testing
        content_preview = str(content)[:50] if content else "empty"
        return f"mock_hash_{self.hash_counter:04d}_{hashlib.md5(content_preview.encode()).hexdigest()[:8]}"

def get_hash_provider() -> HashProvider:
    """Factory function to get the appropriate hash provider."""
    use_mock = os.getenv("USE_MOCK_HASH", "true").lower() == "true"
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development" or use_mock:
        return MockHashProvider()
    else:
        return SHA256HashProvider()
