from abc import ABC, abstractmethod

from src.core.constants import ProcessingStatus
from src.db.repository import Repository
from src.llm.client import LLMClient
from src.llm.model_router import ModelRouter
from src.pipeline.context import PipelineContext


class PipelineStep(ABC):
    name: str
    status_on_start: ProcessingStatus
    status_on_complete: ProcessingStatus
    is_hard_failure: bool = True  # If True, pipeline aborts on failure

    def __init__(
        self,
        llm_client: LLMClient,
        model_router: ModelRouter,
        repo: Repository,
    ):
        self.llm_client = llm_client
        self.model_router = model_router
        self.repo = repo

    @abstractmethod
    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        """Execute this pipeline step, mutating and returning context."""
        ...
