from util import invoke
import pytest

def test_invoke_function():
    result = invoke("echo Hello, World! > hello.txt")
    with open("hello.txt", "r") as f:
        content = f.read().strip()
    assert content == "Hello, World!"

def test_invoke_function_with_error():
    with pytest.raises(RuntimeError, match="Command 'nonexistent_command' failed"):
        invoke("nonexistent_command")
        
def test_runas_command():
    result = invoke("echo Running as command > runas.txt", admin=True)
    with open("runas.txt", "r") as f:
        content = f.read().strip()
    assert content == "Running as command"