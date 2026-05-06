import subprocess
import time
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
EXECUTABLE = PROJECT_DIR / "hangman_buggy_1"


def run_hangman(args=None, stdin=""):
    process = subprocess.Popen(
        [EXECUTABLE] + list(args or []),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert process.stdin is not None
    assert process.stdout is not None
    assert process.stderr is not None

    stdout = ""

    for _ in range(2):
        line = process.stdout.readline()
        if line == "":
            break
        stdout += line

    for guess in stdin.splitlines(True):
        if process.poll() is not None:
            break

        process.stdin.write(guess)
        process.stdin.flush()

        while True:
            line = process.stdout.readline()
            if line == "":
                break

            stdout += line

            if "Guess a letter or try to guess the entire word:" in line:
                break

    time.sleep(0.005)

    if process.poll() is None:
        process.terminate()
        process.wait()

    stderr = process.stderr.read()
    return process.returncode, stdout, stderr


def check_contains(output, expected_parts):
    missing = [part for part in expected_parts if part not in output]
    if missing:
        return [f"missing from stdout: {repr(part)}" for part in missing]
    return []


def check_not_contains(output, forbidden_parts):
    present = [part for part in forbidden_parts if part in output]
    if present:
        return [f"unexpected text in stdout: {repr(part)}" for part in present]
    return []


def check_order(output, expected_parts):
    failures = []
    position = 0

    for part in expected_parts:
        found_at = output.find(part, position)
        if found_at == -1:
            failures.append(
                f"not found in order after position {position}: {repr(part)}"
            )
            break
        position = found_at + len(part)

    return failures


def run_test(test):
    name = test["name"]
    args = test.get("args", [])
    stdin = test.get("stdin", "")

    print(f"\n=== {name} ===")
    print("Command:", [EXECUTABLE] + args)

    try:
        returncode, stdout, stderr = run_hangman(args=args, stdin=stdin)
    except subprocess.TimeoutExpired:
        print("FAIL: application did not finish within the time limit")
        return False
    except FileNotFoundError:
        print(f"FAIL: executable not found: {EXECUTABLE}")
        return False

    failures = []

    expected_exit_code = test.get("expected_exit_code")
    if expected_exit_code is not None and returncode != expected_exit_code:
        failures.append(f"expected exit code {expected_exit_code}, got {returncode}")

    failures.extend(check_contains(stdout, test.get("stdout_contains", [])))
    failures.extend(check_not_contains(stdout, test.get("stdout_not_contains", [])))
    failures.extend(check_order(stdout, test.get("stdout_in_order", [])))

    for text, count in test.get("stdout_counts", {}).items():
        actual = stdout.count(text)
        if actual != count:
            failures.append(f"expected {repr(text)} {count} times, got {actual}")

    for text in test.get("stderr_contains", []):
        if text not in stderr:
            failures.append(f"missing from stderr: {repr(text)}")

    print("Stdout:", repr(stdout))
    print("Stderr:", repr(stderr))
    print("Exit code:", returncode)

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return False

    print("PASS")
    return True


TESTS = [
    {
        "name": "requires exactly one secret word argument",
        "expected_exit_code": 1,
        "stdout_contains": ["Usage:", "<secret word>"],
    },
    {
        "name": "rejects a secret word shorter than 3 letters",
        "args": ["ab"],
        "stdin": "ab\n",
        "expected_exit_code": 1,
        "stdout_contains": [
            "ERROR: The secret word should consist of 3 or more letters!"
        ],
    },
    {
        "name": "rejects a secret word with non-lowercase characters",
        "args": ["abc1"],
        "expected_exit_code": 1,
        "stdout_contains": [
            "ERROR: The secret word should only contain lowercase letters!"
        ],
    },
    {
        "name": "rejects uppercase letters in the secret word",
        "args": ["Test"],
        "expected_exit_code": 1,
        "stdout_contains": [
            "ERROR: The secret word should only contain lowercase letters!"
        ],
    },
    {
        "name": "shows one dot for every hidden letter",
        "args": ["abc"],
        "stdin": "abc\n",
        "expected_exit_code": 0,
        "stdout_in_order": [
            "You have to guess the following word: ...",
            "Guess a letter or try to guess the entire word:",
            "You won, congratulations!",
        ],
        "stdout_not_contains": [
            "You have to guess the following word: ..\n",
            "You have to guess the following word: .. ",
        ],
    },
    {
        "name": "wins immediately when the whole word is guessed",
        "args": ["test"],
        "stdin": "test\n",
        "expected_exit_code": 0,
        "stdout_in_order": [
            "You have to guess the following word: ....",
            "Guess a letter or try to guess the entire word:",
            "You won, congratulations!",
        ],
        "stdout_not_contains": ["That letter is correct!", "You lost."],
    },
    {
        "name": "rejects guesses that are neither one letter nor the whole word",
        "args": ["test"],
        "stdin": "tes\ntest\n",
        "expected_exit_code": 0,
        "stdout_in_order": [
            "ERROR: You can either guess a letter or try to guess the entire word (4 letters).",
            "You won, congratulations!",
        ],
    },
    {
        "name": "counts the first wrong letter as mistake one",
        "args": ["test"],
        "stdin": "z\ntest\n",
        "expected_exit_code": 0,
        "stdout_in_order": [
            "That letter is not correct. You made 1 out of 5 mistakes.",
            "You won, congratulations!",
        ],
        "stdout_not_contains": ["You made 0 out of 5 mistakes."],
    },
    {
        "name": "reveals all copies of a correctly guessed letter",
        "args": ["banana"],
        "stdin": "a\nbanana\n",
        "expected_exit_code": 0,
        "stdout_in_order": [
            "You have to guess the following word: ......",
            "That letter is correct!",
            "You have to guess the following word: .a.a.a",
            "You won, congratulations!",
        ],
    },
    {
        "name": "tracks wrong guesses without revealing the word",
        "args": ["test"],
        "stdin": "a\nk\ne\nt\ns\n",
        "expected_exit_code": 0,
        "stdout_in_order": [
            "That letter is not correct. You made 1 out of 5 mistakes.",
            "That letter is not correct. You made 2 out of 5 mistakes.",
            "That letter is correct!",
            "You have to guess the following word: .e..",
            "That letter is correct!",
            "You have to guess the following word: te.t",
            "You won, congratulations! The secret word was test.",
        ],
    },
    {
        "name": "wins when every distinct letter is guessed individually",
        "args": ["test"],
        "stdin": "t\ne\ns\n",
        "expected_exit_code": 0,
        "stdout_in_order": [
            "You have to guess the following word: t..t",
            "You have to guess the following word: te.t",
            "You won, congratulations! The secret word was test.",
        ],
        "stdout_not_contains": ["You lost."],
    },
    {
        "name": "does not count a repeated correct letter as another guess",
        "args": ["test"],
        "stdin": "t\nt\ne\ns\n",
        "expected_exit_code": 0,
        "stdout_in_order": [
            "That letter is correct!",
            "You have to guess the following word: t..t",
            "ERROR: You already guessed that letter.",
            "You have to guess the following word: t..t",
            "You won, congratulations! The secret word was test.",
        ],
        "stdout_counts": {
            "ERROR: You already guessed that letter.": 1,
            "You made": 0,
        },
    },
    {
        "name": "loses after five wrong letter guesses",
        "args": ["test"],
        "stdin": "z\nq\nx\ny\nw\n",
        "expected_exit_code": 0,
        "stdout_in_order": [
            "That letter is not correct. You made 1 out of 5 mistakes.",
            "That letter is not correct. You made 2 out of 5 mistakes.",
            "That letter is not correct. You made 3 out of 5 mistakes.",
            "That letter is not correct. You made 4 out of 5 mistakes.",
            "You lost. The secret word was test.",
        ],
        "stdout_not_contains": ["You made 5 out of 5 mistakes."],
    },
]


def run_all_tests():
    passed = 0
    for test in TESTS:
        if run_test(test):
            passed += 1

    total = len(TESTS)
    print(f"Passed {passed}/{total} tests")
    return passed == total


if __name__ == "__main__":
    raise SystemExit(0 if run_all_tests() else 1)
