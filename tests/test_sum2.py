import os
import sys
sys.path.append(os.path.dirname(__file__))

from helpers import run_tests

BINARY = os.path.join(os.path.dirname(__file__), "..", "bin", "sum")

test_cases = [
    {"name": "two positives",       "inputs": ["3", "4"],     "expected": 7},
    {"name": "two negatives",       "inputs": ["-3", "-4"],   "expected": -7},
    {"name": "positive + negative", "inputs": ["10", "-3"],   "expected": 7},
    {"name": "zeros",               "inputs": ["0", "0"],     "expected": 0},
    {"name": "large numbers",       "inputs": ["9999", "1"],  "expected": 10000},
]


def main():
    print("=== Testing: sum ===\n")
    run_tests(BINARY, test_cases)


if __name__ == "__main__":
    main()