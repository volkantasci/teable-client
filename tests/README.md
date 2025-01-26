# Teable Client Tests

This directory contains the test suite for the Teable client library. The tests cover all major components of the library following the hierarchical structure: Client -> Space -> Base -> Table -> Record.

## Setup

1. Create a `.env` file in the `tests` directory with the following content:
```
TEABLE_API_KEY=your_api_key_here
TEABLE_API_URL=https://api.teable.io
```

Replace `your_api_key_here` with your actual Teable API key. Note that the API key is scoped to a single space, so all tests will run against that space.

2. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

## Running Tests

To run all tests:
```bash
pytest tests/
```

To run tests for a specific component:
```bash
pytest tests/test_client.py  # Test client functionality
pytest tests/test_space.py   # Test space operations
pytest tests/test_base.py    # Test base operations
pytest tests/test_table.py   # Test table operations
pytest tests/test_record.py  # Test record operations
```

To run tests with verbose output:
```bash
pytest -v tests/
```

## Test Structure

- `test_client.py`: Tests client initialization and configuration
- `test_space.py`: Tests space operations (getting space info, managing bases)
- `test_base.py`: Tests base operations (CRUD, collaborators, permissions)
- `test_table.py`: Tests table operations (CRUD, fields, views, permissions)
- `test_record.py`: Tests record operations (CRUD, batch operations, querying)

Each test file follows a similar pattern:
1. Setup required resources (space, base, table as needed)
2. Execute the test operations
3. Verify the results
4. Clean up created resources

## Important Notes

1. The tests are designed to be idempotent - they clean up after themselves by deleting any resources they create.

2. Due to the API key being scoped to a single space:
   - Space creation/deletion tests are limited
   - Most operations are performed within the authorized space
   - The space ID is obtained from the existing space rather than creating new ones

3. Some tests create temporary resources (bases, tables, records) which are cleaned up even if the test fails.

4. The test suite uses pytest fixtures defined in `conftest.py` to manage common resources and configurations.

5. All tests are independent and can be run in any order.

## Test Coverage

The test suite covers:
- Basic CRUD operations for all resource types
- Batch operations for records
- Query and filter operations
- Permission and collaborator management
- Field and view operations
- Record history and status tracking
- Validation rules and error cases
- Resource relationships and hierarchies
