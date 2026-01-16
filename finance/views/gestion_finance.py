from django.shortcuts import render,  redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from finance.models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

Utilisateur = get_user_model()



class IndexView(View):
    template=  'global_data/index.html'
    def get(self, request):
        user = request.user

        # Récupérer toutes les transactions de l'utilisateur
        transactions = user.transactions.all().order_by('-date')

        # Calculer le solde en partant du solde initial
        solde = getattr(user, 'initial_balance', 0)
        for t in transactions:
            if t.type_transaction == 'REVENU':
                solde += t.montant
            elif t.type_transaction == 'DEPENSE':
                solde -= t.montant
            # ECHEC ou autre type, tu peux ajouter une règle spécifique
            elif t.type_transaction == 'ECHEC':
                solde -= t.montant  # si tu considères l'épargne comme un "débit"

        return render(request, self.template, {
            'user': user,
            'transaction': transactions,
            'solde': solde
        })


class TransactionView(View):
    template= 'global_data/transaction.html'
    def get(self, request):
        user = request.user

        # Récupérer toutes les transactions de l'utilisateur
        transactions = user.transactions.all().order_by('-date')

        # Calculer le solde en partant du solde initial
        solde = getattr(user, 'initial_balance', 0)
        for t in transactions:
            if t.type_transaction == 'REVENU':
                solde += t.montant
            elif t.type_transaction == 'DEPENSE':
                solde -= t.montant
            # ECHEC ou autre type, tu peux ajouter une règle spécifique
            elif t.type_transaction == 'ECHEC':
                solde -= t.montant  # si tu considères l'épargne comme un "débit"

        return render(request, self.template, {
            'user': user,
            'transaction': transactions,
            'solde': solde
        })





class AccountView(View):
    template= 'global_data/account.html'
    def get(self, request):
        return render(request,self.template )


class AddView(View):
    template= 'global_data/add.html'
    def get(self, request):
        return render(request, self.template)
    
    def post(self, request):
        user = request.user
        type_transaction = request.POST.get('type_transaction')
        montant = float(request.POST.get('montant', 0))
        compte = request.POST.get('compte')
        categorie = request.POST.get('categorie')
        description = request.POST.get('description')

        # Calculer le solde actuel
        transactions = user.transactions.all()
        solde = getattr(user, 'initial_balance', 0)
        for t in transactions:
            if t.type_transaction == 'REVENU':
                solde += t.montant
            elif t.type_transaction == 'DEPENSE':
                solde -= t.montant
            elif t.type_transaction == 'ECHEC':
                solde -= t.montant  # si on considère l'épargne comme un débit

        # Vérifier si le solde est suffisant pour une dépense
        if type_transaction == 'DEPENSE' and montant > solde:
            messages.error(request, "Vous n'avez pas assez de solde pour effectuer cette dépense !")
            return redirect('add')  # ou reste sur le formulaire

        # Créer la transaction
        Transaction.objects.create(
            utilisateur=user,
            type_transaction=type_transaction,
            montant=montant,
            compte=compte,
            categorie=categorie,
            description=description
        )

        messages.success(request, f"{type_transaction.capitalize()} de {montant} CFA ajouté avec succès !")
        return redirect('index')