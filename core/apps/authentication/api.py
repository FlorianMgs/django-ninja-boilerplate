from ninja import Router, Schema
from django.contrib.auth import get_user_model
from .authentication import api_key_auth
from .schemas import UserProfileSchema, APIKeyRegenSchema

User = get_user_model()
router = Router(tags=["Authentication"])


@router.get("/me", response=UserProfileSchema, auth=api_key_auth)
def get_user_profile(request):
    """Get current user profile"""
    return UserProfileSchema(
        id=str(request.auth.id),
        username=request.auth.username,
        email=request.auth.email,
        is_staff=request.auth.is_staff,
        api_key=request.auth.api_key,
    )


@router.post("/regenerate-key", response=APIKeyRegenSchema, auth=api_key_auth)
def regenerate_api_key(request):
    """Regenerate API key for current user"""
    request.auth.regenerate_api_key()
    request.auth.refresh_from_db()  # Get updated api_key from database

    return APIKeyRegenSchema(
        message="API key regenerated successfully",
        new_api_key=request.auth.api_key,
    )
