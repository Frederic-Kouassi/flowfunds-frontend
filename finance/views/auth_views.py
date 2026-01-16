from django.shortcuts import render,  redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from finance.models import Utilisateur,Compte
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

Utilisateur = get_user_model()


class RegisterView(View):
    template_name = 'auth/register.html'

    def get(self, request):
        # Affiche le formulaire d'inscription
        return render(request, self.template_name)

    def post(self, request):
    # Récupération des données du formulaire
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')  # 🔹 ajouté
        phone_number = request.POST.get('phone_number')
        initial_balance = request.POST.get('initial_balance')  
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Vérification que tous les champs sont remplis
        if not all([first_name, last_name, phone_number, initial_balance, password, password_confirm]):
            messages.error(request, "Veuillez remplir tous les champs.")
            return render(request, self.template_name)

        # Vérification que les mots de passe correspondent
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, self.template_name)

        # Vérification que le numéro de téléphone n'existe pas déjà
        if Utilisateur.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Ce numéro de téléphone est déjà utilisé.")
            return render(request, self.template_name)

        # Conversion de l'initial_balance en float
        try:
            initial_balance = float(initial_balance)
        except ValueError:
            messages.error(request, "Le solde initial doit être un nombre valide.")
            return render(request, self.template_name)

        # Création de l'utilisateur
        user = Utilisateur.objects.create_user(
            first_name=first_name,
            last_name=last_name,  # 🔹 ajouté
            phone_number=phone_number,
            initial_balance=initial_balance,
            password=password
        )

        messages.success(request, "Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
        return redirect('login')



class LoginView(View):
    template_name = 'auth/login.html'

    def get(self, request):
        # Affiche le formulaire de connexion
        return render(request, self.template_name)

    def post(self, request):
        # Récupération des données du formulaire
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        if not all([phone_number, password]):
            messages.error(request, "Veuillez remplir tous les champs.")
            return render(request, self.template_name)

        # Authentification
        user = authenticate(request, phone_number=phone_number, password=password)
        if user is not None:
            login(request, user)  # Connexion de l'utilisateur
            messages.success(request, f"Bienvenue {user.first_name} !")
            return redirect('index')  # Redirige vers la page d'accueil ou dashboard
        else:
            messages.error(request, "Numéro de téléphone ou mot de passe incorrect.")
   
        return render(request, self.template_name)
    

class LogoutView(View):
    def get(self, request):
        logout(request)  
        messages.success(request, "Vous avez été déconnecté avec succès.")
        return redirect('login')  
    
    



@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'auth/profile.html'

    def get(self, request):
        # Récupérer tous les comptes liés de l'utilisateur
        linked_accounts = Compte.objects.filter(user=request.user)
        user= request.user
        return render(request, self.template_name, {
            'linked_accounts': linked_accounts,
            'user':user
        })

    def post(self, request):
        # 🔹 Détecter si c'est un POST pour le profil ou pour un compte
        if 'full_name' in request.POST:  # Modification du profil
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')

            user = request.user

            # Mise à jour du nom complet
            if full_name:
                name_parts = full_name.strip().split(' ', 1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''

            if email:
                user.email = email

            if phone:
                user.phone_number = phone

            user.save()
            messages.success(request, "Profil mis à jour avec succès !")
            return redirect('profile')

        elif 'account_type' in request.POST:  # Création d'un nouveau compte
            account_type = request.POST.get('account_type')
            phone = request.POST.get('phone')
            label = request.POST.get('label')

            if not account_type or not phone or not label:
                messages.error(request, "Veuillez remplir tous les champs.")
            else:
                Compte.objects.create(
                    user=request.user,
                    type_compte=account_type,
                    phone=phone,
                    label=label
                )
                messages.success(request, " Compte ajouté avec succès !")
                return redirect('profile')

        # Si erreur, renvoyer la liste actuelle des comptes
        linked_accounts = Compte.objects.filter(user=request.user)
        return render(request, self.template_name, {
            'linked_accounts': linked_accounts
        })

