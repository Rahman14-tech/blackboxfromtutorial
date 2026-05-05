import subprocess
import sys
import os


def main():
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    test_files = sorted(f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py"))

    if not test_files:
        print("No test files found.")
        sys.exit(1)

    all_passed = True

    for test_file in test_files:
        path = os.path.join(test_dir, test_file)
        print(f"\nRunning {test_file}...")
        print("-" * 40)

        result = subprocess.run([sys.executable, path])

        if result.returncode != 0:
            all_passed = False

    print("\n" + "=" * 40)
    if all_passed:
        print("ALL TEST SUITES PASSED")
    else:
        print("SOME TEST SUITES FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()