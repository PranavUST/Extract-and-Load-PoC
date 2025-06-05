import pytest
from retry_utils import retry

def test_retry_success_first_try():
    calls = []
    @retry(retries=3, delay=0)
    def func():
        calls.append(1)
        return "ok"
    assert func() == "ok"
    assert len(calls) == 1

def test_retry_success_after_failures(monkeypatch):
    calls = []
    @retry(retries=3, delay=0)
    def func():
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("fail")
        return "ok"
    assert func() == "ok"
    assert len(calls) == 2

def test_retry_raises_after_all_failures(monkeypatch):
    calls = []
    @retry(retries=3, delay=0)
    def func():
        calls.append(1)
        raise RuntimeError("fail")
    with pytest.raises(RuntimeError):
        func()
    assert len(calls) == 3

def test_retry_only_catches_specified_exceptions():
    calls = []
    @retry(retries=3, delay=0, exceptions=(ValueError,))
    def func():
        calls.append(1)
        raise TypeError("fail")
    with pytest.raises(TypeError):
        func()
    assert len(calls) == 1

def test_retry_delay(monkeypatch):
    called = []
    def fake_sleep(seconds):
        called.append(seconds)
    monkeypatch.setattr("time.sleep", fake_sleep)
    count = {"n": 0}
    @retry(retries=2, delay=5)
    def func():
        count["n"] += 1
        raise Exception("fail")
    with pytest.raises(Exception):
        func()
    assert called == [5]