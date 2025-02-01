import pytest
from teable.models.view import View, FilterOperator, SortDirection, Position, FilterCondition, SortCondition

def test_view_from_api_response():
    # Test data
    api_response = {
        'id': 'view123',
        'name': 'Test View',
        'description': 'Test Description',
        'filter': [
            {
                'fieldId': 'field1',
                'operator': '=',
                'value': 'test'
            }
        ],
        'sort': [
            {
                'fieldId': 'field2',
                'direction': 'asc'
            }
        ]
    }
    
    # Create view from response
    view = View.from_api_response(api_response)
    
    # Verify basic properties
    assert view.view_id == 'view123'
    assert view.name == 'Test View'
    assert view.description == 'Test Description'
    
    # Verify filters
    assert len(view.filters) == 1
    filter_condition = view.filters[0]
    assert filter_condition.field == 'field1'
    assert filter_condition.operator == FilterOperator.EQUALS
    assert filter_condition.value == 'test'
    
    # Verify sorts
    assert len(view.sorts) == 1
    sort_condition = view.sorts[0]
    assert sort_condition.field == 'field2'
    assert sort_condition.direction == SortDirection.ASCENDING

def test_view_to_dict():
    # Create a view
    view = View(
        view_id='view123',
        name='Test View',
        description='Test Description'
    )
    
    # Convert to dict
    result = view.to_dict()
    
    # Verify dict structure
    assert result == {
        'id': 'view123',
        'name': 'Test View',
        'description': 'Test Description'
    }

def test_view_create_query():
    # Create a view with filters and sorts
    view = View(
        view_id='view123',
        name='Test View',
        filters=[
            FilterCondition(
                field='field1',
                operator=FilterOperator.EQUALS,
                value='test'
            )
        ],
        sorts=[
            SortCondition(
                field='field2',
                direction=SortDirection.ASCENDING
            )
        ]
    )
    
    # Create query builder
    query = view.create_query()
    
    # Verify query builder state
    assert query.view_id == 'view123'
    assert len(query.filters) == 1
    assert len(query.sorts) == 1
    
    # Build query params
    params = query.build()
    assert params['viewId'] == 'view123'
    assert len(params['filter']) == 1
    assert len(params['sort']) == 1

def test_view_update_order():
    # Create a view with mock client
    class MockClient:
        def _make_request(self, method, url, json):
            assert method == 'PUT'
            assert url == 'table/table123/view/view123/order'
            assert json == {
                'anchorId': 'anchor123',
                'position': 'before'
            }
    
    view = View(
        view_id='view123',
        name='Test View',
        _client=MockClient()
    )
    
    # Update order
    view.update_order(
        table_id='table123',
        anchor_id='anchor123',
        position=Position.BEFORE
    )

def test_view_from_api_response_empty_filters():
    # Test with empty filters and sorts
    api_response = {
        'id': 'view123',
        'name': 'Test View'
    }
    
    view = View.from_api_response(api_response)
    assert len(view.filters) == 0
    assert len(view.sorts) == 0

def test_view_from_api_response_invalid_filter():
    # Test with invalid filter format
    api_response = {
        'id': 'view123',
        'name': 'Test View',
        'filter': 'invalid'  # String instead of list
    }
    
    # Artık hata fırlatmak yerine boş liste döndürüyor
    view = View.from_api_response(api_response)
    assert len(view.filters) == 0
