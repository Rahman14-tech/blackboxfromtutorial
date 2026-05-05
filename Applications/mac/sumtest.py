import subprocess
import threading

test_cases = [
    {"name": "two positives",       "input1": "3",    "input2": "4",    "expected": 7},
    {"name": "two negatives",       "input1": "-3",   "input2": "-4",   "expected": -7},
    {"name": "positive + negative", "input1": "10",   "input2": "-3",   "expected": 7},
    {"name": "zeros",               "input1": "0",    "input2": "0",    "expected": 0},
    {"name": "large numbers",       "input1": "9999", "input2": "1",    "expected": 10000},
]


def run_test(test):
    process = subprocess.Popen(
        ["./sum"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    timed_out = False

    def kill_process():
        nonlocal timed_out
        timed_out = True
        process.kill()

    timer = threading.Timer(5, kill_process)
    timer.start()

    try:
        process.stdout.readline()
        process.stdin.write(test["input1"] + "\n")
        process.stdin.flush()

        process.stdout.readline()
        process.stdin.write(test["input2"] + "\n")
        process.stdin.flush()

        result = int(process.stdout.readline())

        if result == test["expected"]:
            print(f"[PASS] {test['name']}")
            return True
        else:
            print(f"[FAIL] {test['name']}: expected {test['expected']}, got {result}")
            return False

    except ValueError:
        if timed_out:
            print(f"[FAIL] {test['name']}: timed out after 5 seconds")
        else:
            print(f"[FAIL] {test['name']}: output was not a valid integer")
        return False

    except OSError:
        print(f"[FAIL] {test['name']}: process crashed or could not start")
        return False

    finally:
        timer.cancel()
        try:
            process.kill()
            process.wait()
        except OSError:
            pass


def main():
    passed = 0
    failed = 0

    for test in test_cases:
        if run_test(test):
            passed += 1
        else:
            failed += 1

    print(f"\n--- Summary ---")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")


if __name__ == "__main__":
    main()