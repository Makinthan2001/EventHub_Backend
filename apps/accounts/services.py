from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError

User = get_user_model()

def user_create(*, email: str, password: str, full_name: str, **extra_fields) -> User:
    user = User(email=email, full_name=full_name, **extra_fields)
    user.set_password(password)
    user.full_clean()
    user.save()
    return user

@transaction.atomic
def user_update(*, user: User, data) -> User:
    for field, value in data.items():
        setattr(user, field, value)
    
    user.full_clean()
    user.save()
    return user

def user_toggle_status(*, user: User) -> bool:
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    return user.is_active

def user_change_role(*, user: User, role: str) -> User:
    if role not in dict(User.ROLE_CHOICES):
        raise ValidationError(f"Invalid role: {role}")
    
    user.role = role
    user.is_staff = (role == 'admin')
    user.save(update_fields=['role', 'is_staff'])
    return user

def user_change_password(*, user: User, new_password: str) -> None:
    user.set_password(new_password)
    user.save(update_fields=['password'])
