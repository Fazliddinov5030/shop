from django.conf import settings

class LanguageMiddleware:
    allowed_languages = {'uz', 'ru', 'en'}
    default_language = 'uz'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.GET.get('lang')
        if lang in self.allowed_languages:
            request.session['language'] = lang
        request.language_code = request.session.get('language', self.default_language)
        response = self.get_response(request)
        return response
