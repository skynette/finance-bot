from django.contrib.auth import get_user_model
User = get_user_model()

class UserService:
    @staticmethod
    def get_or_create_user_by_telegram_id(tg_id: int, first_name: str = "", username: str = ""):
        from django.db.models import Q
        user, created = User.objects.get_or_create(
            telegram_id=tg_id,
            defaults={"first_name": first_name, "username": username}
        )
        return user