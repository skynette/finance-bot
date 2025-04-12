from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    telegram_first_name = models.CharField(max_length=255, null=True, blank=True)
    telegram_last_name = models.CharField(max_length=255, null=True, blank=True)
    telegram_photo_url = models.URLField(max_length=512, null=True, blank=True)
    telegram_language_code = models.CharField(max_length=10, null=True, blank=True)
    is_telegram_user = models.BooleanField(default=False)
    telegram_auth_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        if self.telegram_username:
            return f"@{self.telegram_username}"
        return self.username

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5, blank=True)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        ordering = ['code']
    
    def __str__(self):
        if self.symbol:
            return f"{self.code} ({self.symbol})"
        return self.code
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Currency.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_default(cls):
        """Get the default currency, or the first one if no default exists"""
        default = cls.objects.filter(is_default=True).first()
        if not default:
            default = cls.objects.first()
        return default

def get_default_currency():
    """Function to get the default currency ID for use in models"""
    return Currency.get_default().id if Currency.get_default() else None

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(
        Currency, 
        on_delete=models.PROTECT, 
        related_name='incomes',
        default=get_default_currency
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='incomes', default=None, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Income'
        verbose_name_plural = 'Incomes'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.amount} {self.currency.code} - {self.category.name} ({self.date.strftime('%Y-%m-%d')})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('income-detail', args=[str(self.id)])
    

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(
        Currency, 
        on_delete=models.PROTECT, 
        related_name='expenses',
        default=get_default_currency
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='expenses', default=None, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.amount} {self.currency.code} - {self.category.name}"