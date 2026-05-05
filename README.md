# Black Box Testing Framework

A Python-based black box testing framework for testing command-line applications using subprocess. The framework treats each application as a black box — it sends inputs and verifies outputs without knowing the internal implementation.


## Adding Executables

Place your compiled binaries in the `bin/` directory and give them execute permission:

```bash
cp /path/to/your/executable ./bin/
chmod +x bin/*
```

## Running Tests

Run all tests:
```bash
python run_tests.py
```

Run a specific test file:
```bash
python tests/test_sum.py
```