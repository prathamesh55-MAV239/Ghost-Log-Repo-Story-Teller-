import subprocess
import os
from datetime import datetime

# Minimal pytest stub
class _RaisesContext:
    def __init__(self, exc_type):
        self.exc_type = exc_type
        self.value = None
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, tb):
        if exc_type is None:
            raise AssertionError(f"{self.exc_type.__name__} not raised")
        if not issubclass(exc_type, self.exc_type):
            raise AssertionError(f"Unexpected exception {exc_type}")
        self.value = exc_val
        return True

class _DummyMark:
    @staticmethod
    def parametrize(argnames, argvalues):
        def decorator(func):
            return func
        return decorator

class pytest:
    mark = _DummyMark()
    @staticmethod
    def raises(exc_type):
        return _RaisesContext(exc_type)

from ghost_story import Commit, GhostLogError, get_commit_log

def test_commit_witching_hour_detection_cases():
    cases = [(0, True), (1, True), (2, True), (3, True), (4, True), (5, False), (23, False)]
    for hour, expected in cases:
        dt = datetime(2023, 1, 1, hour, 0)
        commit = Commit(short_hash="abc123", author="Alice", date=dt, message="msg")
        assert commit.is_witching_hour == expected

def test_get_commit_log_no_path():
    with pytest.raises(GhostLogError) as exc:
        get_commit_log("")
    assert "No repository path was given" in str(exc.value)

def test_get_commit_log_path_not_dir():
    import tempfile, shutil, os
    # create a temporary directory and a file inside it
    tmp_dir = tempfile.mkdtemp()
    file_path = os.path.join(tmp_dir, "somefile.txt")
    with open(file_path, "w") as f:
        f.write("content")
    try:
        with pytest.raises(GhostLogError) as exc:
            get_commit_log(file_path)
        assert "isn't a folder" in str(exc.value)
    finally:
        shutil.rmtree(tmp_dir)

def _fake_run_file_not_found(*args, **kwargs):
    raise FileNotFoundError()

def _fake_run_timeout(*args, **kwargs):
    raise subprocess.TimeoutExpired(cmd=args[0], timeout=15)

def test_get_commit_log_git_not_installed():
    original = subprocess.run
    subprocess.run = _fake_run_file_not_found
    try:
        with pytest.raises(GhostLogError) as exc:
            get_commit_log(os.getcwd())
        assert "git isn't installed" in str(exc.value)
    finally:
        subprocess.run = original

def test_get_commit_log_timeout():
    original = subprocess.run
    subprocess.run = _fake_run_timeout
    try:
        with pytest.raises(GhostLogError) as exc:
            get_commit_log(os.getcwd())
        assert "Reading the git log timed out" in str(exc.value)
    finally:
        subprocess.run = original
