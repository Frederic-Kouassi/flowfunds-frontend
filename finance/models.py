from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
from django.db import models
from django_extensions.db.models import ActivatorModel, TimeStampedModel
from django.conf import settings


class BlogBaseModel(ActivatorModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True


# 🔹 UserManager personnalisé
class UtilisateurManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone_number, password=None, first_name=None, last_name=None, initial_balance=0, **extra_fields):
        """
        Crée et sauvegarde un utilisateur avec les informations données.
        """
        if not phone_number:
            raise ValueError("Le numéro de téléphone doit être renseigné")
        
        # Normalisation facultative du numéro de téléphone
        phone_number = str(phone_number).strip()
        
        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            initial_balance=initial_balance,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True")
        
        return self.create_user(phone_number, password, **extra_fields)


# 🔹 Modèle utilisateur
class Utilisateur(AbstractUser, BlogBaseModel):
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Phone number"
    )
    
    # Prénom / Nom
    first_name = models.CharField(max_length=150, verbose_name="First Name")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Last Name")

    # Solde initial
    initial_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        verbose_name="Initial Balance"
    )

    username = None
    email = models.EmailField(blank=True, null=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []  # Aucun champ requis pour create_superuser hormis phone_number et password

    objects = UtilisateurManager()  # 🔹 lie le manager personnalisé

    def __str__(self):
        return self.phone_number


class Compte(models.Model):
    ACCOUNT_TYPES = [
        ('MTN', 'MTN Mobile Money'),
        ('Orange', 'Orange Money'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='linked_accounts'
    )

    type_compte = models.CharField(
        max_length=10,
        choices=ACCOUNT_TYPES
    )

    phone = models.CharField(
        max_length=20
    )

    label = models.CharField(
        max_length=50
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
     return f"{self.get_type_compte_display()} - {self.phone}"  # <-- idem

    
    
class Transaction(BlogBaseModel):
    TYPE_TRANSACTION = [
        ('REVENU', 'Revenu'),
        ('DEPENSE', 'Dépense'),
        ('ECHEC', 'Épargne'),
    ]

    COMPTES = [
        ('Especes', 'Especes'),
        ('momo', 'MoMo'),
        ('orange', 'Orange Money'),
        ('banque', 'Épargne bancaire'),
    ]

    CATEGORIES = [
        ('nourriture', 'Alimentation & Restaurants'),
        ('transport', 'Transport'),
        ('shopping', 'Shopping'),
        ('loisirs', 'Loisirs & Divertissement'),
        ('factures', 'Factures & Services'),
        ('sante', 'Santé'),
        ('education', 'Éducation'),
        ('autre', 'Autre'),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    type_transaction = models.CharField(
        max_length=10,
        choices=TYPE_TRANSACTION,
        default='DEPENSE',
        verbose_name="Type de transaction"
    )
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant (CFA)"
    )
    compte = models.CharField(
        max_length=20,
        choices=COMPTES,
        verbose_name="Compte"
    )
    categorie = models.CharField(
        max_length=50,
        choices=CATEGORIES,
        verbose_name="Catégorie"
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Description"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date"
    )

    class Meta:
        ordering = ['-date']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.get_type_transaction_display()} - {self.montant} CFA - {self.compte}"

    # 🔹 Surcharge de save() pour mettre à jour le solde utilisateur
    def save(self, *args, **kwargs):
        # Vérifie si c'est une nouvelle transaction
        is_new = self.pk is None

        super().save(*args, **kwargs)  # on sauvegarde d'abord pour générer la PK si nouvelle

        if is_new:
            user = self.utilisateur
            # On initialise le balance si inexistant
            if not hasattr(user, 'balance'):
                user.balance = getattr(user, 'initial_balance', 0)

            # Met à jour le solde selon le type
            if self.type_transaction == 'DEPENSE':
                user.balance -= self.montant
            elif self.type_transaction == 'REVENU':
                user.balance += self.montant
            elif self.type_transaction == 'ECHEC':  # Épargne, à adapter selon logique
                user.balance -= self.montant

   