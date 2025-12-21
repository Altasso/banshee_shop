from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve


class OrderVerificationMiddleware:
    VERIFICATION_REQUIRED_URLS = [
        "order-create",
        "order-checkout",
        "cart-checkout",
        "checkout",
        "order-payment",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticatedand and not request.user.is_verified:
            try:
                url_name = resolve(request.path_info).url_name
            except:
                url_name = None

            if url_name in self.VERIFICATION_REQUIRED_URLS:
                messages.warning(
                    request,
                    "⚠️ Для оформления заказа необходимо подтвердить email. "
                    "Проверьте почту и перейдите по ссылке из письма.",
                )

                return redirect('cart')

            response = self.get_response(request)
            return response
