from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Currency, Category, Income, Expense

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Telegram Information', {'fields': (
            'telegram_id', 
            'telegram_username', 
            'telegram_first_name', 
            'telegram_last_name',
            'telegram_photo_url',
            'telegram_language_code',
            'is_telegram_user',
            'telegram_auth_date'
        )}),
    )
    list_display = UserAdmin.list_display + ('telegram_username', 'is_telegram_user')
    search_fields = UserAdmin.search_fields + ('telegram_username', 'telegram_id')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Currency)
admin.site.register(Category)
admin.site.register(Income)
admin.site.register(Expense)