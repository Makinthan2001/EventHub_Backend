from django.contrib.auth import get_user_model
from django.db.models import QuerySet

User = get_user_model()

def user_list() -> QuerySet:
    return User.objects.filter(role='organizer')

def user_get_by_id(user_id: int) -> User:
    return User.objects.get(id=user_id)
