from django.shortcuts import render,  redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models import Q

from finance.models import *

from django.contrib.auth.mixins import LoginRequiredMixin


Utilisateur = get_user_model()


class IndexView(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'global_data/index.html'

    def get(self, request):
        user = request.user
        transactions = user.transactions.all().order_by('-date')

        # 🔹 Fonction utilitaire pour calculer le solde par compte
        def solde(compte):
            revenus = user.transactions.filter(
                compte=compte,
                type_transaction='REVENU'
            ).aggregate(total=Sum('montant'))['total'] or 0

            depenses = user.transactions.filter(
                compte=compte,
                type_transaction='DEPENSE'
            ).aggregate(total=Sum('montant'))['total'] or 0

            return revenus - depenses

        # 🔹 Soldes par compte
        solde_cash = solde('Especes')
        solde_momo = solde('momo')
        solde_orange = solde('orange')

        # 🔹 Argent utilisable
        usable_money = solde_cash + solde_momo + solde_orange

        # 🔹 Épargne (Savings)
        
        

        return render(request, self.template_name, {
            'solde_cash': solde_cash,
            'solde_momo': solde_momo,
            'solde_orange': solde_orange,
             'transaction': transactions,
              'usable_money': usable_money,
            
        })
   



class TransactionView(View):
    template = 'global_data/transaction.html'

    def get(self, request):
        user = request.user

        # Récupérer tous les paramètres de recherche
        query = request.GET.get('q', '')       # mot-clé
        type_filter = request.GET.get('type', '')  # type de transaction

        # Base : toutes les transactions de l'utilisateur
        transactions = user.transactions.all().order_by('-date')

        # Filtrer par type si sélectionné
        if type_filter:
            type_mapping = {
                'income': 'REVENU',
                'expense': 'DEPENSE',
                'save': 'ECHEC'
            }
            transactions = transactions.filter(type_transaction=type_mapping.get(type_filter))

        # Filtrer par mot-clé si fourni (sur description ou catégorie)
        if query:
            transactions = transactions.filter(
                Q(description__icontains=query) |
                Q(categorie__icontains=query)
            )

        # Calculer le solde en partant du solde initial
        solde = getattr(user, 'initial_balance', 0)
        for t in transactions:
            if t.type_transaction == 'REVENU':
                solde += t.montant
            elif t.type_transaction == 'DEPENSE':
                solde -= t.montant
            elif t.type_transaction == 'ECHEC':
                solde -= t.montant  # Épargne considérée comme "débit"

        return render(request, self.template, {
            'user': user,
            'transaction': transactions,
            'solde': solde,
            'query': query,
            'type_filter': type_filter,
        })




class AccountView(LoginRequiredMixin, View):
    template = 'global_data/account.html'

    def get(self, request):
        user = request.user

        # 🔹 Fonction utilitaire pour calculer le solde par compte
        def solde(compte):
            revenus = user.transactions.filter(
                compte=compte,
                type_transaction='REVENU'
            ).aggregate(total=Sum('montant'))['total'] or 0

            depenses = user.transactions.filter(
                compte=compte,
                type_transaction='DEPENSE'
            ).aggregate(total=Sum('montant'))['total'] or 0

            return revenus - depenses

        # 🔹 Soldes par compte
        solde_cash = solde('Especes')
        solde_momo = solde('momo')
        solde_orange = solde('orange')

        # 🔹 Argent utilisable
        usable_money = solde_cash + solde_momo + solde_orange

        # 🔹 Épargne (Savings)
        epargne = user.transactions.filter(
            type_transaction='ECHEC'
        ).aggregate(total=Sum('montant'))['total'] or 0

        # 🔹 Valeur nette
        net_worth = usable_money + epargne

        return render(request, self.template, {
            'solde_cash': solde_cash,
            'solde_momo': solde_momo,
            'solde_orange': solde_orange,
            'usable_money': usable_money,
            'epargne': epargne,
            'net_worth': net_worth,
        })

class AddView(View):
    template = 'global_data/add.html'

    def get(self, request):
        return render(request, self.template)
    
    def post(self, request):
        user = request.user
        type_transaction = request.POST.get('type_transaction')
        compte = request.POST.get('compte')
        categorie = request.POST.get('categorie')
        description = request.POST.get('description')

        # 🔹 Récupérer le montant et vérifier qu'il est positif
        try:
            montant = float(request.POST.get('montant', 0))
            if montant <= 0:
                messages.error(request, "Le montant doit être supérieur à 0 !")
                return redirect('add')
        except ValueError:
            messages.error(request, "Montant invalide !")
            return redirect('add')

        # 🔹 Calculer le solde du compte sélectionné
        revenus = user.transactions.filter(
            compte=compte,
            type_transaction='REVENU'
        ).aggregate(total=Sum('montant'))['total'] or 0

        depenses = user.transactions.filter(
            compte=compte,
            type_transaction__in=['DEPENSE', 'ECHEC']
        ).aggregate(total=Sum('montant'))['total'] or 0

        solde_compte = revenus - depenses

        # 🔹 Vérifier si solde suffisant pour une dépense
        if type_transaction == 'DEPENSE' and montant > solde_compte:
            messages.error(request, f"Solde insuffisant pour le compte {compte.upper()} ! Solde actuel : {solde_compte} FCFA")
            return redirect('add')

        # 🔹 Créer la transaction
        Transaction.objects.create(
            utilisateur=user,
            type_transaction=type_transaction,
            montant=montant,
            compte=compte,
            categorie=categorie,
            description=description
        )

        messages.success(request, f"{type_transaction.capitalize()} de {montant} FCFA ajouté avec succès !")
        return redirect('index')