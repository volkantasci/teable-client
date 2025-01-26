"""Test utilities."""
import time

def wait_for_records(client, table_id, expected_count=None, max_retries=5, delay=1, **query_params):
    """Wait for records to be indexed and available.
    
    Args:
        client: Authenticated client instance
        table_id: ID of the table to check
        expected_count: Expected number of non-empty records
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        List[Record]: List of non-empty records
        
    Raises:
        AssertionError: If expected count not reached after max retries
    """
    for _ in range(max_retries):
        all_records = client.records.get_records(table_id, **query_params)
        # Filter out system-generated empty records and ensure fields have values
        non_empty_records = [
            r for r in all_records 
            if r.get("fields") and any(v for v in r["fields"].values())
        ]
        if expected_count is None or len(non_empty_records) == expected_count:
            return non_empty_records
        time.sleep(delay)
    
    if expected_count is not None:
        raise AssertionError(
            f"Expected {expected_count} records but found {len(non_empty_records)} "
            f"after {max_retries} retries"
        )
    return non_empty_records
