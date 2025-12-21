from django import forms
from django.forms import inlineformset_factory

from products.models import Category, Product, Service, ProductIMG


class ProductForm(forms.ModelForm):
    class Meta:
        models = Product
        fields = [
            "name",
            "description",
            "base_price",
            "discount_price",
            "is_unique",
            "stock_quantity",
            "category_id",
            "is_active",
            "manufacturing_time_days",
            "materials",
            "weight",
            "size",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название продукта"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Описание продукта",
                    "rows": 4,
                }
            ),
            "base_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Базовая цена"}
            ),
            "discount_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Цена со скидкой"}
            ),
            "is_unique": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "stock_quantity": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Количество на складе"}
            ),
            "category_id": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "manufacturing_time_days": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Дней на изготовление"}
            ),
            "materials": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Материалы"}
            ),
            "weight": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Вес (кг)"}
            ),
            "size": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Размер"}
            ),
        }

    def clean_discount_price(self):
        base_price = self.cleaned_data.get("base_price")
        discount_price = self.cleaned_data.get("discount_price")

        if discount_price and base_price and discount_price > base_price:
            raise forms.ValidationError(
                "Цена со скидкой не может быть больше базовой цены"
            )
        return discount_price

    def clean_stock_quantity(self):
        stock_quantity = self.cleaned_data.get("stock_quantity")

        if stock_quantity < 0:
            raise forms.ValidationError(
                "Количество на складе не может быть отрицательным"
            )
        return stock_quantity


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "slug"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название категории"}
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Описание категории",
                    "rows": 4,
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "URL slug (например: figure)",
                }
            ),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")

        if not slug.instance.pk:
            if Category.objects.filter(slug=slug).exists():
                raise forms.ValidationError("Категория с таким slug уже существует")
            else:
                if (
                    Category.objects.filter(slug=slug)
                    .exclude(pk=slug.instance.pk)
                    .exists()
                ):
                    raise forms.ValidationError("Категория с таким slug уже существует")

        return slug


class ProductImageForm(forms.ModelForm):
    """Форма для изображения продукта"""

    class Meta:
        model = ProductIMG
        fields = ["image_url", "is_main", "order"]
        widgets = {
            "image_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com/image.jpg",
                }
            ),
            "is_main": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }
        labels = {
            "image_url": "URL изображения",
            "is_main": "Главное фото",
            "order": "Порядок",
        }


# Формсет для изображений продукта
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductIMG,
    form=ProductImageForm,
    extra=3,  # Количество пустых форм
    can_delete=True,
    max_num=10,  # Максимум 10 изображений
    validate_max=True,
)


class ServiceForm(forms.ModelForm):
    """Форма для создания/редактирования услуги"""

    class Meta:
        model = Service
        fields = ["name", "description", "price", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название услуги"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Описание услуги",
                }
            ),
            "price": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": "Название",
            "description": "Описание",
            "price": "Стоимость (₽)",
            "is_active": "Активна",
        }


class StockUpdateForm(forms.Form):
    """Форма для обновления количества товара на складе"""

    ACTION_CHOICES = [
        ("add", "Добавить"),
        ("subtract", "Вычесть"),
        ("set", "Установить"),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Действие",
    )

    quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Количество"}
        ),
        label="Количество",
    )


class ProductFilterForm(forms.Form):
    """Форма для фильтрации продуктов"""

    STATUS_CHOICES = [
        ("", "Все"),
        ("active", "Активные"),
        ("inactive", "Неактивные"),
        ("out_of_stock", "Нет в наличии"),
    ]

    SORT_CHOICES = [
        ("-created_at", "Новые первые"),
        ("created_at", "Старые первые"),
        ("name", "По названию (А-Я)"),
        ("-name", "По названию (Я-А)"),
        ("base_price", "По цене (возр.)"),
        ("-base_price", "По цене (убыв.)"),
        ("stock_quantity", "По остатку (возр.)"),
        ("-stock_quantity", "По остатку (убыв.)"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Статус",
    )

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial="-created_at",
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Сортировка",
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Поиск по названию или описанию",
            }
        ),
        label="Поиск",
    )


class ReviewFilterForm(forms.Form):
    """Форма для фильтрации отзывов"""

    STATUS_CHOICES = [
        ("", "Все"),
        ("pending", "Ожидают верификации"),
        ("verified", "Верифицированные"),
    ]

    RATING_CHOICES = [
        ("", "Все рейтинги"),
        ("5", "5 звезд"),
        ("4", "4 звезды"),
        ("3", "3 звезды"),
        ("2", "2 звезды"),
        ("1", "1 звезда"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Статус",
    )

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Рейтинг'
    )