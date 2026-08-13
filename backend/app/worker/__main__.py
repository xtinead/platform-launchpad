import logging
import os

from app.worker.runner import DeploymentWorkerRunner


DEFAULT_POLL_INTERVAL_SECONDS = 5.0


def configure_logging() -> None:
    """Configure worker-process logging."""

    logging.basicConfig(
        level=os.getenv(
            "WORKER_LOG_LEVEL",
            "INFO",
        ).upper(),
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s"
        ),
    )


def get_poll_interval() -> float:
    """Read and validate the worker polling interval."""

    raw_value = os.getenv(
        "WORKER_POLL_INTERVAL_SECONDS",
        str(DEFAULT_POLL_INTERVAL_SECONDS),
    )

    try:
        poll_interval = float(raw_value)
    except ValueError as exc:
        raise ValueError(
            "WORKER_POLL_INTERVAL_SECONDS must be numeric."
        ) from exc

    if poll_interval <= 0:
        raise ValueError(
            "WORKER_POLL_INTERVAL_SECONDS must be greater than zero."
        )

    return poll_interval


def main() -> None:
    """Start the deployment worker process."""

    configure_logging()

    runner = DeploymentWorkerRunner(
        poll_interval_seconds=get_poll_interval(),
    )

    runner.run_forever()


if __name__ == "__main__":
    main()