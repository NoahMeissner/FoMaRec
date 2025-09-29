# Noah Meissner 11.08.2025

from dataclasses import dataclass
from typing import Optional


@dataclass
class ManagerStep:
    """Represents a single step in the Manager's reasoning process"""
    step_number: int
    thought: str
    action: str
    observation: Optional[str] = None
    is_final: bool = False
