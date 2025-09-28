from typing import Dict, Literal
from huggingface_hub import HfApi, ModelInfo
import time
from metrics.base import *

HardwareType = Literal["jetson_nano", "raspberry_pi", "desktop_pc", "aws_server"]

# Max "suitable" model sizes per hardware in MB
HARDWARE_SIZE_LIMITS: Dict[HardwareType, int] = {
    "jetson_nano": 250,
    "raspberry_pi": 100,
    "desktop_pc": 2000,
    "aws_server": 5000,
}

class SizeScore(Metric):

    def calculate(self) -> float:
        start_time: float = time.time()
        _ = self.score_model_size()

        score: float = 0.1 * self.scores['raspberry_pi'] + 0.3 * self.scores['jetson_nano'] + 0.3 * self.scores['desktop_pc'] + 0.3 * self.scores['aws_server']

        self.score = score 
        self.latency = int((time.time() - start_time) * 1000)
        return score 


    def normalize_size_score(self, model_size_mb: float, max_size_mb: int) -> float:
        """
        Returns a float between 0 and 1 depending on how well the model size fits
        within the max suitable size for a given hardware.
        Linear decay: full score if <= max_size, zero if >= 2x max_size.
        """
        if model_size_mb <= max_size_mb:
            return 1.0
        elif model_size_mb >= 2 * max_size_mb:
            return 0.0
        else:
            excess = model_size_mb - max_size_mb
            return 1.0 - (excess / max_size_mb)


    def get_model_size_mb(self) -> float:
        model_id = self.asset_id
        api: HfApi = HfApi()
        info: ModelInfo = api.model_info(model_id)
        
        total_bytes: int = sum(s.size for s in info.siblings if s.size is not None)
        return total_bytes / 1_000_000  # bytes to MB


    def score_model_size(self) -> Dict[HardwareType, float]:
        model_id = self.asset_id
        """
        Given a Hugging Face model ID, returns a dictionary mapping hardware types
        to a float score between 0 and 1 indicating model size suitability.
        """
        model_size_mb: float = self.get_model_size_mb(model_id)

        hardware_scores = {
            hardware: self.normalize_size_score(model_size_mb, max_size)
            for hardware, max_size in HARDWARE_SIZE_LIMITS.items()
        }

        self.scores = hardware_scores

        return hardware_scores
