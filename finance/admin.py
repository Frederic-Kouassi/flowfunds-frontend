from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Utilisateur

@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    model = Utilisateur
    list_display = ('phone_number', 'is_active', 'is_staff', 'is_superuser')
    ordering = ('phone_number',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )
