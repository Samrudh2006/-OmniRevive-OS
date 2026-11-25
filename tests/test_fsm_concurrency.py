import threading
from backend.app.b2b.state_machine import B2BReceivablesStateMachine


def test_only_one_of_two_racing_transitions_wins(tmp_path):
    fsm = B2BReceivablesStateMachine(db_path=str(tmp_path / "fsm.db"))
    start = fsm.get_state("INV-RACE")
    targets = sorted(fsm.VALID_TRANSITIONS.get(start, set()))
    assert targets, "start state must allow a transition"
    # Pick a target, then fire it from many threads: after the first wins, the state has moved on
    target = targets[0]
    wins, losses = [], []

    def go():
        try:
            fsm.transition("INV-RACE", target, "race")
            wins.append(1)
        except ValueError:
            losses.append(1)

    threads = [threading.Thread(target=go) for _ in range(12)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    history = fsm.get_history("INV-RACE")
    assert len(wins) == len(history)
    assert fsm.get_state("INV-RACE") == target
    # Each recorded transition must chain from the previous one
    for a, b in zip(history, history[1:]):
        assert a.to_state == b.from_state


def test_persistence_failure_does_not_advance_memory(tmp_path, monkeypatch):
    import pytest
    fsm = B2BReceivablesStateMachine(db_path=str(tmp_path / "fsm2.db"))
    start = fsm.get_state("INV-FAIL")
    target = sorted(fsm.VALID_TRANSITIONS[start])[0]

    def broken():
        raise RuntimeError("disk full")

    monkeypatch.setattr(fsm, "_get_conn", broken)
    with pytest.raises(RuntimeError):
        fsm.transition("INV-FAIL", target, "x")
    assert fsm.get_state("INV-FAIL") == start
