"""Test suite for Space operations."""
import pytest
from teable.models.space import Space, SpaceRole
from teable.exceptions import ValidationError

def test_get_space_info(authenticated_client):
    """Test retrieving space information."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Test Space")
    assert isinstance(space, Space)
    assert space.name == "Test Space"
    
    # Get all spaces (should include our new space)
    spaces = authenticated_client.spaces.get_spaces()
    assert len(spaces) > 0
    assert any(s.name == "Test Space" for s in spaces)
    
    # Clean up
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_space_get_bases(authenticated_client):
    """Test retrieving bases in the space."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Base Test Space")
    
    # Get bases (should be empty initially)
    bases = space.get_bases()
    assert len(bases) == 0
    
    # Create a base
    base = space.create_base(name="Test Base")
    
    # Get bases again
    bases = space.get_bases()
    assert len(bases) == 1
    assert bases[0].name == "Test Base"
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_space_create_base(authenticated_client):
    """Test creating a base in the space."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Create Base Test Space")
    
    # Create a base
    base = space.create_base(name="Test Base")
    assert base.name == "Test Base"
    assert base.space_id == space.space_id
    
    # Clean up
    base.delete()
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_space_get_collaborators(authenticated_client):
    """Test retrieving space collaborators."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Collaborator Test Space")
    
    # Get collaborators
    collaborators, total = space.get_collaborators()
    assert len(collaborators) >= 1  # Should include at least the creator
    assert total >= 1
    
    # Clean up
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_space_get_invitation_links(authenticated_client):
    """Test retrieving space invitation links."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Invitation Test Space")
    
    # Get invitation links (should be empty initially)
    invitations = space.get_invitation_links()
    assert len(invitations) == 0
    
    # Create an invitation link
    invitation = space.create_invitation_link(role=SpaceRole.EDITOR)
    assert invitation.role == SpaceRole.EDITOR
    assert hasattr(invitation, 'invite_url')
    
    # Get invitation links again
    invitations = space.get_invitation_links()
    assert len(invitations) == 1
    
    # Clean up
    authenticated_client.spaces.delete_invitation(space.space_id, invitation.invitation_id)
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_space_invite_by_email(authenticated_client):
    """Test inviting users by email."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Email Invite Test Space")
    
    # Send invitation emails
    result = space.invite_by_email(
        emails=["test@example.com"],
        role=SpaceRole.EDITOR
    )
    assert len(result) == 1
    assert "test@example.com" in result
    
    # Clean up
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_space_validation(authenticated_client):
    """Test space validation rules."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Validation Test Space")
    
    # Test invalid role
    with pytest.raises(ValidationError):
        space.create_invitation_link(role="invalid_role")
    
    # Test invalid email
    with pytest.raises(ValidationError):
        space.invite_by_email(
            emails=["invalid_email"],
            role=SpaceRole.EDITOR
        )
    
    # Clean up
    authenticated_client.spaces.permanently_delete_space(space.space_id)

def test_space_update_name(authenticated_client):
    """Test updating space name."""
    # Create a space first
    space = authenticated_client.spaces.create_space(name="Original Name")
    
    # Update name
    space.update("Updated Name")
    
    # Get space again to verify
    updated_space = authenticated_client.spaces.get_space(space.space_id)
    assert updated_space.name == "Updated Name"
    
    # Clean up
    authenticated_client.spaces.permanently_delete_space(space.space_id)
