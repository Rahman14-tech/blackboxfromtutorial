import subprocess
import threading


def run_process(binary_path, inputs, timeout=5):
    """Run a binary, send inputs line by line, return the last line of output."""
    process = subprocess.Popen(
        [binary_path],
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

    timer = threading.Timer(timeout, kill_process)
    timer.start()

    try:
        for value in inputs:
            process.stdout.readline()           # read the prompt
            process.stdin.write(value + "\n")    # send input
            process.stdin.flush()

        result = process.stdout.readline().strip()
        return {"success": True, "output": result}

    except Exception:
        if timed_out:
            return {"success": False, "error": "timed out"}
        return {"success": False, "error": "process crashed"}

    finally:
        timer.cancel()
        try:
            process.kill()
            process.wait()
        except OSError:
            pass


def run_tests(binary_path, test_cases):
    passed = 0
    failed = 0

    for test in test_cases:
        result = run_process(binary_path, test["inputs"], test.get("timeout", 5))

        if not result["success"]:
            print(f"[FAIL] {test['name']}: {result['error']}")
            failed += 1
            continue

        try:
            actual = int(result["output"])
        except ValueError:
            print(f"[FAIL] {test['name']}: output '{result['output']}' is not a valid integer")
            failed += 1
            continue

        if actual == test["expected"]:
            print(f"[PASS] {test['name']}")
            passed += 1
        else:
            print(f"[FAIL] {test['name']}: expected {test['expected']}, got {actual}")
            failed += 1

    print("\n --- Summary --- ")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")

    return failed == 0