import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SlopRankLogger")

@dataclass
class EvalConfig:
    """Configuration for the SlopRank evaluation system."""
    model_names: List[str]
    evaluation_method: int  # 1 => numeric rating, 2 => up/down (example usage)
    use_subset_evaluation: bool
    evaluators_subset_size: int
    output_dir: Path
    request_delay: float = 0.0

    def __post_init__(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.evaluation_method not in {1, 2}:
            raise ValueError("evaluation_method must be 1 or 2")
        if self.evaluators_subset_size >= len(self.model_names):
            raise ValueError("evaluators_subset_size must be < number of models")

DEFAULT_CONFIG = EvalConfig(
    model_names=[
        # OpenAI GPT models
        "gpt-4o",
        "gpt-5",
        "gpt-5-mini",
        "gpt-5-nano",
        "o1-preview",
        "o3",
        "o4-mini",

        # Anthropic Claude models
        "claude-opus-4-20250514",
        "claude-sonnet-4-20250514",
        "claude-sonnet-4-5-20250929",  # Sonnet 4.5
        "claude-haiku-4-5",             # Haiku 4.5

        # Google Gemini models
        "gemini-exp-1206",
        "gemini-2.0-flash-thinking-exp-1219",
        "gemini-2.5-pro-preview-06-05",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",

        # DeepSeek models
        "deepseek-chat",
        "deepseek-reasoner",
    ],
    evaluation_method=1,  # numeric
    use_subset_evaluation=True,
    evaluators_subset_size=3,
    output_dir=Path("results"),
    request_delay=0.0
)
