from ninja import Schema


class UserProfileSchema(Schema):
    id: str
    username: str
    email: str
    is_staff: bool
    api_key: str


class APIKeyRegenSchema(Schema):
    message: str
    new_api_key: str
