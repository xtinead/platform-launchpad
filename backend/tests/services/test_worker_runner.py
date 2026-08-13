import pytest

from app.worker.runner import DeploymentWorkerRunner


class FakeSession:
    """Minimal context-manager session used by runner tests."""

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        return None


def test_runner_rejects_nonpositive_poll_interval() -> None:
    with pytest.raises(
        ValueError,
        match="poll interval must be greater than zero",
    ):
        DeploymentWorkerRunner(
            poll_interval_seconds=0,
        )


def test_runner_rejects_invalid_max_iterations() -> None:
    runner = DeploymentWorkerRunner(
        poll_interval_seconds=1,
    )

    with pytest.raises(
        ValueError,
        match="max iterations must be at least one",
    ):
        runner.run_forever(max_iterations=0)


def test_runner_stops_after_requested_iterations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_count = 0
    sleep_calls: list[float] = []

    runner = DeploymentWorkerRunner(
        poll_interval_seconds=2.5,
        sleep_function=sleep_calls.append,
    )

    def fake_run_once() -> None:
        nonlocal run_count
        run_count += 1
        return None

    monkeypatch.setattr(
        runner,
        "run_once",
        fake_run_once,
    )

    runner.run_forever(max_iterations=3)

    assert run_count == 3
    assert sleep_calls == [2.5, 2.5]


def test_runner_stop_prevents_additional_iterations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_count = 0

    runner = DeploymentWorkerRunner(
        poll_interval_seconds=1,
        sleep_function=lambda _: None,
    )

    def fake_run_once() -> None:
        nonlocal run_count
        run_count += 1
        runner.stop()
        return None

    monkeypatch.setattr(
        runner,
        "run_once",
        fake_run_once,
    )

    runner.run_forever()

    assert run_count == 1
    assert runner.stop_event.is_set()


def test_runner_handles_keyboard_interrupt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = DeploymentWorkerRunner(
        poll_interval_seconds=1,
        sleep_function=lambda _: None,
    )

    def interrupt() -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(
        runner,
        "run_once",
        interrupt,
    )

    runner.run_forever()

    assert not runner.stop_event.is_set()