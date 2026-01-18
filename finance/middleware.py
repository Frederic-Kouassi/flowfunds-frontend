from django.shortcuts import redirect

class ForceLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si l'utilisateur est connecté → OK
        if request.user.is_authenticated:
            return self.get_response(request)

        # URLs publiques autorisées même si non connecté
        public_paths = [
            '/login/',
            '/register/',
        ]

        # Autoriser toutes les URLs admin
        if request.path.startswith('/admin/') or request.path in public_paths:
            return self.get_response(request)

        # Sinon redirection vers login
        return redirect('/login/')
