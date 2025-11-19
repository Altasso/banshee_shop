from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from users.services.address_autocomplete import AddressAutocompleteService


class AddressAutocompleteView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('query', '')
        count = int(request.GET.get('count', 10))

        if len(query) < 3:
            return JsonResponse({'suggestions': []})
        suggestions = AddressAutocompleteService.get_suggestions(query, count)

        return JsonResponse({'suggestions': suggestions})
