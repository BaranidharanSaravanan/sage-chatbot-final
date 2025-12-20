from src.generation.generator import Generator
from unittest.mock import patch
import subprocess


def fake_subprocess_run_success(*args, **kwargs):
    class FakeResult:
        def __init__(self):
            self.stdout = b"The library is open from 8 AM to 8 PM on weekdays."
            self.stderr = b""
    return FakeResult()


def fake_subprocess_run_error(*args, **kwargs):
    raise FileNotFoundError()


@patch("subprocess.run", side_effect=fake_subprocess_run_success)
def test_generator_with_mocked_llm(mock_run):
    gen = Generator()
    answer = gen.generate(
        "What are the library working hours?",
        ["Library timings are available."]
    )
    assert "8 AM" in answer


def test_empty_context_refusal():
    gen = Generator()
    answer = gen.generate("What is hostel curfew?", [])
    assert "don't have" in answer.lower()


@patch("subprocess.run", side_effect=fake_subprocess_run_error)
def test_model_not_available(mock_run):
    gen = Generator()
    answer = gen.generate(
        "What are the library hours?",
        ["Library timings exist."]
    )
    assert "model not available" in answer.lower()
