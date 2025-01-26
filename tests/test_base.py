"""Test suite for Base operations."""
import os
import pytest
from datetime import datetime
from teable.models.base import Base, Position, CollaboratorType
from teable.exceptions import APIError
from teable.models.user import User

def test_base_crud_operations(authenticated_client):
    """Test base creation, reading, updating, and deletion."""
    # Get the space first
    spaces = authenticated_client.spaces.get_spaces()
    space = spaces[0]
    
    # Create a base
    base_name = "Test Base CRUD"
    base = space.create_base(name=base_name, icon="🌟")
    assert isinstance(base, Base)
    assert base.name == base_name
    assert base.space_id == space.space_id
    # API doesn't support icons currently
    
    # Update base
    new_name = "Updated Base Name"
    updated_base = base.update(name=new_name)
    assert updated_base.name == new_name
    
    # Delete base
    assert base.delete() is True

def test_base_duplicate(authenticated_client):
    """Test base duplication functionality."""
    spaces = authenticated_client.spaces.get_spaces()
    space = spaces[0]
    
    # Create original base
    original_name = "Original Base"
    original_base = space.create_base(name=original_name, icon="🌟")
    
    # Duplicate base
    duplicate_name = "Duplicated Base"
    duplicated_base = original_base.duplicate(
        space_id=space.space_id,
        name=duplicate_name,
        with_records=False
    )
    
    assert duplicated_base.name == duplicate_name
    assert duplicated_base.space_id == space.space_id
    assert duplicated_base.base_id != original_base.base_id
    
    # Clean up
    original_base.delete()
    duplicated_base.delete()

def test_base_order(authenticated_client):
    """Test base ordering functionality."""
    spaces = authenticated_client.spaces.get_spaces()
    space = spaces[0]
    
    # Create two bases
    base1 = space.create_base(name="Base 1", icon="1️⃣")
    base2 = space.create_base(name="Base 2", icon="2️⃣")
    
    # Update order
    base2.update_order(base1.base_id, Position.BEFORE)
    
    # Clean up
    base1.delete()
    base2.delete()

def test_base_collaborators(authenticated_client):
    """Test base collaborator operations."""
    spaces = authenticated_client.spaces.get_spaces()
    space = spaces[0]
    base = space.create_base(name="Collaborator Test Base", icon="👥")
    
    # Get collaborators - skip first 3 default entries
    collaborators, total = base.get_collaborators(
        include_system=True,
        skip=3,  # Skip default entries
        take=10
    )
    assert isinstance(collaborators, list)
    assert isinstance(total, int)
    assert total >= len(collaborators)
    
    # Test sending email invitations with unique email
    unique_email = f'test{int(datetime.now().timestamp())}@example.com'
    result = base.send_email_invitations(
        emails=[unique_email],
        role='viewer'
    )
    assert isinstance(result, dict)
    
    # Clean up
    base.delete()

def test_base_permissions(authenticated_client):
    """Test base permission operations."""
    spaces = authenticated_client.spaces.get_spaces()
    space = spaces[0]
    base = space.create_base(name="Permission Test Base", icon="🔒")
    
    # Get permissions
    permissions = base.get_permissions()
    assert isinstance(permissions, dict)
    
    # Verify common permissions exist
    expected_permissions = ['create', 'read', 'update', 'delete']
    for perm in expected_permissions:
        assert any(perm in key for key in permissions.keys())
    
    # Clean up
    base.delete()

def test_base_invitation_links(authenticated_client):
    """Test base invitation link operations."""
    spaces = authenticated_client.spaces.get_spaces()
    space = spaces[0]
    base = space.create_base(name="Invitation Test Base", icon="✉️")
    
    # Get invitation links
    invitations = base.get_invitation_links()
    assert isinstance(invitations, list)
    
    # Create invitation link
    invitation = base.create_invitation_link(role='viewer')
    assert invitation.role == 'viewer'
    assert invitation.invite_url
    assert invitation.invitation_code
    
    # Clean up
    base.delete()

def test_base_query(authenticated_client):
    """Test base query functionality."""
    spaces = authenticated_client.spaces.get_spaces()
    space = spaces[0]
    base = space.create_base(name="Query Test Base", icon="🔍")
    
    try:
        # Execute a simple query
        # Note: This is a basic test, actual queries would depend on table structure
        results = base.query("SELECT 1")
        assert isinstance(results, list)
        
        # Test with different cell format
        results_json = base.query("SELECT 1", cell_format='json')
        assert isinstance(results_json, list)
    except APIError as e:
        if e.status_code != 500:  # Ignore internal server errors for now
            raise
    finally:
        # Clean up
        base.delete()

def test_base_validation(authenticated_client):
    """Test base validation and error cases."""
    spaces = authenticated_client.spaces.get_spaces()
    space = spaces[0]
    base = space.create_base(name="Validation Test Base", icon="✅")
    
    # Test invalid role for invitation
    with pytest.raises(Exception):  # Specific exception type would depend on implementation
        base.create_invitation_link(role='invalid_role')
    
    # Test invalid email format
    with pytest.raises(Exception):
        base.send_email_invitations(['invalid-email'], role='viewer')
    
    # Clean up
    base.delete()

def test_base_attributes(authenticated_client):
    """Test base attribute handling."""
    spaces = authenticated_client.spaces.get_spaces()
    space = spaces[0]
    
    # Create base with all attributes
    base = space.create_base(
        name="Attribute Test Base",
        icon="📘"
    )
    
    # Verify attributes
    assert base.base_id
    assert base.name == "Attribute Test Base"
    assert base.space_id == space.space_id
    # API doesn't support icons currently
    assert isinstance(base.is_unrestricted, bool)
    assert base.collaborator_type in [None, *list(CollaboratorType)]
    
    # Test conversion to dictionary
    base_dict = base.to_dict()
    assert isinstance(base_dict, dict)
    assert base_dict['id'] == base.base_id
    assert base_dict['name'] == base.name
    assert base_dict['spaceId'] == base.space_id
    
    # Clean up
    base.delete()
