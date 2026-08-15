import logging
import threading
from collections.abc import Callable
from time import sleep

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.deployment_request import DeploymentRequest
from app.services.deployment_executor import DeploymentExecutor
from app.services.deployment_worker_service import (
    DeploymentWorkerService,
)


logger = logging.getLogger(__name__)

SessionFactory = Callable[[], Session]
SleepFunction = Callable[[float], None]


class DeploymentWorkerRunner:
    """Continuously poll for and process queued deployment requests."""

    def __init__(
        self,
        *,
        session_factory: SessionFactory = SessionLocal,
        executor: DeploymentExecutor | None = None,
        poll_interval_seconds: float = 5.0,
        sleep_function: SleepFunction = sleep,
    ) -> None:
        if poll_interval_seconds <= 0:
            raise ValueError(
                "Worker poll interval must be greater than zero."
            )

        self.session_factory = session_factory
        self.executor = executor or DeploymentExecutor()
        self.poll_interval_seconds = poll_interval_seconds
        self.sleep_function = sleep_function
        self.stop_event = threading.Event()

    def run_once(self) -> DeploymentRequest | None:
        """Process at most one queued deployment request."""

        with self.session_factory() as session:
            worker_service = DeploymentWorkerService(
                session,
                executor=self.executor,
            )

            deployment_request = (
                worker_service.process_next_request()
            )

            if deployment_request is None:
                logger.debug("No queued deployment request found.")
                return None

            logger.info(
                "Processed deployment request %s with status %s.",
                deployment_request.id,
                deployment_request.status,
            )

            return deployment_request

    def run_forever(
        self,
        *,
        max_iterations: int | None = None,
    ) -> None:
        """
        Poll continuously until stopped.

        `max_iterations` exists primarily for controlled execution and
        automated testing. Production workers normally leave it unset.
        """

        if max_iterations is not None and max_iterations < 1:
            raise ValueError(
                "Worker max iterations must be at least one."
            )

        logger.info(
            "Deployment worker started with poll interval %.2f seconds.",
            self.poll_interval_seconds,
        )

        iteration_count = 0

        try:
            while not self.stop_event.is_set():
                self.run_once()
                iteration_count += 1

                if (
                    max_iterations is not None
                    and iteration_count >= max_iterations
                ):
                    break

                if not self.stop_event.is_set():
                    self.sleep_function(
                        self.poll_interval_seconds
                    )
        except KeyboardInterrupt:
            logger.info(
                "Deployment worker interrupted by the operator."
            )
        finally:
            logger.info("Deployment worker stopped.")

    def stop(self) -> None:
        """Request graceful worker shutdown."""

        self.stop_event.set()