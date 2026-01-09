import unittest
from unittest.mock import Mock, MagicMock
from teable.core.fields import FieldManager
from teable.core.views import ViewManager
from teable.core.tables import TableManager
from teable.models.field import Field, FieldType
from teable.models.view import View
from teable.exceptions import ValidationError

class TestFieldViewTableUnit(unittest.TestCase):
    def setUp(self):
        self.mock_http = Mock()
        self.mock_cache = MagicMock()
        self.field_manager = FieldManager(self.mock_http, self.mock_cache)
        self.view_manager = ViewManager(self.mock_http, self.mock_cache)
        self.table_manager = TableManager(self.mock_http, self.mock_cache)

    def test_create_field(self):
        table_id = "tbl123"
        self.mock_http.request.return_value = {
            "id": "fld123",
            "name": "New Field",
            "type": "singleLineText",
            "isPrimary": False,
            "description": "desc"
        }
        
        field = self.field_manager.create_field(
            table_id, 
            "singleLineText",
            name="New Field",
            description="desc"
        )
        
        self.mock_http.request.assert_called_with(
            "POST",
            f"/table/{table_id}/field",
            json={
                "type": "singleLineText",
                "name": "New Field",
                "description": "desc"
            }
        )
        self.assertEqual(field.field_id, "fld123")
        self.assertEqual(field.name, "New Field")

    def test_create_view(self):
        table_id = "tbl123"
        self.mock_http.request.return_value = {
            "id": "viw123",
            "name": "Grid View",
            "type": "grid",
            "description": "My View"
        }
        
        view = self.view_manager.create_view(
            table_id,
            "Grid View",
            "grid",
            description="My View"
        )
        
        self.mock_http.request.assert_called_with(
            "POST",
            f"/table/{table_id}/view",
            json={
                "name": "Grid View",
                "type": "grid",
                "description": "My View"
            }
        )
        self.assertEqual(view.view_id, "viw123")
        self.assertEqual(view.name, "Grid View")

    def test_delete_view(self):
        table_id = "tbl123"
        view_id = "viw123"
        
        self.view_manager.delete_view(table_id, view_id)
        
        self.mock_http.request.assert_called_with(
            "DELETE",
            f"/table/{table_id}/view/{view_id}"
        )

    def test_update_view(self):
        table_id = "tbl123"
        view_id = "viw123"
        self.mock_http.request.return_value = {
            "id": "viw123",
            "name": "Updated View"
        }
        
        self.view_manager.update_view(
            table_id,
            view_id,
            name="Updated View"
        )
        
        self.mock_http.request.assert_called_with(
            "PATCH",
            f"/table/{table_id}/view/{view_id}",
            json={"name": "Updated View"}
        )

    def test_update_view_order(self):
        table_id = "tbl123"
        view_id = "viw123"
        
        self.view_manager.update_view_order(
            table_id,
            view_id,
            anchor_id="viw456",
            position="after"
        )
        
        self.mock_http.request.assert_called_with(
            "PUT",
            f"/table/{table_id}/view/{view_id}/order",
            json={
                "anchorId": "viw456",
                "position": "after"
            }
        )

    def test_archive_table(self):
        base_id = "base123"
        table_id = "tbl123"
        
        self.table_manager.archive_table(base_id, table_id)
        
        self.mock_http.request.assert_called_with(
            "POST",
            f"/base/{base_id}/table/{table_id}/archive"
        )

    def test_unarchive_table(self):
        base_id = "base123"
        table_id = "tbl123"
        
        self.table_manager.unarchive_table(base_id, table_id)
        
        self.mock_http.request.assert_called_with(
            "POST",
            f"/base/{base_id}/table/{table_id}/unarchive"
        )

if __name__ == '__main__':
    unittest.main()
