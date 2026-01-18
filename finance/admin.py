from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Utilisateur, Transaction, Compte


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
@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_compte_affichage', 'phone', 'label', 'created_at')

    def type_compte_affichage(self, obj):
        return obj.get_type_compte_display()  # <-- ici le nom exact du champ
    type_compte_affichage.short_description = 'Type de compte'



# 🔹 Admin pour le modèle Transaction
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'type_transaction', 'montant', 'compte', 'categorie', 'date')
    list_filter = ('type_transaction', 'compte', 'categorie')
    search_fields = ('utilisateur__phone_number', 'description')