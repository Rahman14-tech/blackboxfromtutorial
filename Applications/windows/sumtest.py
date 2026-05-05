import subprocess
from unittest import result

print("TEST: check if the application can add two positive integers")


def test_sum(a, b):
    process = subprocess.Popen(["../bin/sum"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)

    process.stdout.readline()  # Read the initial prompt
    process.stdin.write(f"{a}\n")  # Input the first number
    process.stdin.flush()

    process.stdout.readline()  # Read the second prompt
    process.stdin.write(f"{b}\n")  # Input the second number
    process.stdin.flush()

    result = float(process.stdout.readline())  # Read the result and convert to float

    return result

def main():
    first_test = test_sum(7,4)
    if first_test == 11:
        print("TEST PASSED")
    else:
        print("TEST FAILED: got", first_test, "expected 11")
    # You can add more tests here if you want

if __name__ == "__main__":
    main()

