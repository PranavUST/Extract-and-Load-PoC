import pytest
from retry_utils import retry, retry_call

def test_retry_call_success_first_try(monkeypatch):
    calls = []
    def func():
        calls.append(1)
        return "ok"
    assert retry_call(func, retries=3, delay=0) == "ok"
    assert len(calls) == 1

def test_retry_call_success_after_failures(monkeypatch):
    calls = []
    def func():
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("fail")
        return "ok"
    assert retry_call(func, retries=3, delay=0, exceptions=(ValueError,)) == "ok"
    assert len(calls) == 2

def test_retry_call_raises_after_all_failures(monkeypatch):
    calls = []
    def func():
        calls.append(1)
        raise RuntimeError("fail")
    with pytest.raises(RuntimeError):
        retry_call(func, retries=3, delay=0, exceptions=(RuntimeError,))
    assert len(calls) == 3

def test_retry_call_only_catches_specified_exceptions():
    calls = []
    def func():
        calls.append(1)
        raise TypeError("fail")
    with pytest.raises(TypeError):
        retry_call(func, retries=3, delay=0, exceptions=(ValueError,))
    assert len(calls) == 1

def test_retry_call_delay(monkeypatch):
    called = []
    def fake_sleep(seconds):
        called.append(seconds)
    monkeypatch.setattr("time.sleep", fake_sleep)
    count = {"n": 0}
    def func():
        count["n"] += 1
        raise Exception("fail")
    with pytest.raises(Exception):
        retry_call(func, retries=2, delay=5)
    assert called == [5]

def test_retry_decorator_success_first_try():
    calls = []
    @retry(retries=3, delay=0)
    def func():
        calls.append(1)
        return "ok"
    assert func() == "ok"
    assert len(calls) == 1

def test_retry_decorator_success_after_failures():
    calls = []
    @retry(retries=3, delay=0, exceptions=(ValueError,))
    def func():
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("fail")
        return "ok"
    assert func() == "ok"
    assert len(calls) == 2

def test_retry_decorator_raises_after_all_failures():
    calls = []
    @retry(retries=3, delay=0, exceptions=(RuntimeError,))
    def func():
        calls.append(1)
        raise RuntimeError("fail")
    with pytest.raises(RuntimeError):
        func()
    assert len(calls) == 3

def test_retry_decorator_only_catches_specified_exceptions():
    calls = []
    @retry(retries=3, delay=0, exceptions=(ValueError,))
    def func():
        calls.append(1)
        raise TypeError("fail")
    with pytest.raises(TypeError):
        func()
    assert len(calls) == 1

def test_retry_decorator_delay(monkeypatch):
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