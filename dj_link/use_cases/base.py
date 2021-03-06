"""Contains the abstract base classes use-cases inherit from."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Generic, TypeVar

from ..base import Base

if TYPE_CHECKING:
    from . import RepositoryLink, RepositoryLinkFactory

LOGGER = logging.getLogger(__name__)


class AbstractRequestModel(ABC):  # pylint: disable=too-few-public-methods
    """ABC for request models."""


RequestModel = TypeVar("RequestModel", bound=AbstractRequestModel)


class AbstractResponseModel(ABC):  # pylint: disable=too-few-public-methods
    """ABC for response models."""


class AbstractUseCase(ABC, Base, Generic[RequestModel]):
    """Specifies the interface for use-cases."""

    name: str

    def __init__(
        self, repo_link_factory: RepositoryLinkFactory, output_port: Callable[[AbstractResponseModel], None]
    ) -> None:
        """Initialize the use-case."""
        self.repo_link_factory = repo_link_factory
        self.output_port = output_port

    def __call__(self, request_model: RequestModel) -> None:
        """Execute the use-case and passes the response model to the output port."""
        LOGGER.info(f"Executing {self.name} use-case...")
        response_model = self.execute(self.repo_link_factory(), request_model)
        LOGGER.info(f"Finished executing {self.name} use-case!")
        self.output_port(response_model)

    @abstractmethod
    def execute(self, repo_link: RepositoryLink, request_model: RequestModel) -> AbstractResponseModel:
        """Execute the use-case."""
