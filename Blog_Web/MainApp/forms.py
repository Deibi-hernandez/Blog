from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["titulo", "contenido"]
        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Escribe el título de tu post...",
            }),
            "contenido": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Escribe el contenido aquí...",
            }),
        }
        labels = {
            "titulo": "Título",
            "contenido": "Contenido",
        }


class PostFilterForm(forms.Form):
    autor = forms.ChoiceField(
        required=False,
        label="Filtrar por autor",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    fecha_desde = forms.DateField(
        required=False,
        label="Desde",
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        }),
    )
    fecha_hasta = forms.DateField(
        required=False,
        label="Hasta",
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        }),
    )

    def __init__(self, *args, **kwargs):
        from django.contrib.auth.models import User
        super().__init__(*args, **kwargs)
        # Poblar dinámicamente el select de autores con los que tienen posts
        autores = User.objects.filter(posts__isnull=False).distinct()
        choices = [("", "Todos los autores")]
        choices += [(u.id, u.get_full_name() or u.username) for u in autores]
        self.fields["autor"].choices = choices


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Tu nombre de usuario",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Tu contraseña",
        }),
    )


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Elige un nombre de usuario",
        }),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "tu@email.com",
        }),
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Crea una contraseña segura",
        }),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Repite la contraseña",
        }),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]