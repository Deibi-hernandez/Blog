from django.shortcuts import render

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

from .models import Post
from .forms import PostForm, PostFilterForm, CustomAuthenticationForm, CustomUserCreationForm


# ──────────────────────────────────────────────
# Mixin reutilizable: autor o admin pueden actuar
# ──────────────────────────────────────────────
class AutorRequiredMixin(UserPassesTestMixin):
    """Permite el acceso al autor del post o a administradores."""
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.autor or self.request.user.is_superuser


# ──────────────────────────────────────────────
# Lista de posts con filtros
# ──────────────────────────────────────────────
class PostListView(ListView):
    model = Post
    template_name = "index.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        qs = super().get_queryset()
        form = PostFilterForm(self.request.GET or None)

        if form.is_valid():
            autor_id = form.cleaned_data.get("autor")
            fecha_desde = form.cleaned_data.get("fecha_desde")
            fecha_hasta = form.cleaned_data.get("fecha_hasta")

            if autor_id:
                qs = qs.filter(autor_id=autor_id)
            if fecha_desde:
                qs = qs.filter(fecha_creacion__date__gte=fecha_desde)
            if fecha_hasta:
                qs = qs.filter(fecha_creacion__date__lte=fecha_hasta)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = PostFilterForm(self.request.GET or None)
        return context


# ──────────────────────────────────────────────
# Detalle de un post
# ──────────────────────────────────────────────
class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"


# ──────────────────────────────────────────────
# Crear un post (requiere login)
# ──────────────────────────────────────────────
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "formulario_post.html"

    def form_valid(self, form):
        # Asignar automáticamente el autor al usuario autenticado
        form.instance.autor = self.request.user
        messages.success(self.request, "✅ Post publicado con éxito.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_formulario"] = "Crear nuevo post"
        context["accion"] = "Publicar"
        return context


# ──────────────────────────────────────────────
# Editar un post (sólo el autor)
# ──────────────────────────────────────────────
class PostUpdateView(LoginRequiredMixin, AutorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "formulario_post.html"

    def form_valid(self, form):
        messages.success(self.request, "✏️ Post actualizado correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_formulario"] = "Editar post"
        context["accion"] = "Guardar cambios"
        return context


# ──────────────────────────────────────────────
# Eliminar un post (sólo el autor)
# ──────────────────────────────────────────────
class PostDeleteView(LoginRequiredMixin, AutorRequiredMixin, DeleteView):
    model = Post
    template_name = "confirmar_borrado.html"
    success_url = reverse_lazy("blog:post_list")
    context_object_name = "post"

    def form_valid(self, form):
        messages.success(self.request, "🗑️ Post eliminado correctamente.")
        return super().form_valid(form)


# ──────────────────────────────────────────────
# Autenticación
# ──────────────────────────────────────────────
class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = "login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"👋 Bienvenido, {form.get_user().username}!")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("blog:post_list")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "Sesión cerrada. ¡Hasta pronto!")
        return super().dispatch(request, *args, **kwargs)


# ──────────────────────────────────────────────
# Registro de usuarios
# ──────────────────────────────────────────────
class CustomUserCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registro.html"
    success_url = reverse_lazy("blog:login")

    def form_valid(self, form):
        messages.success(self.request, "✅ ¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.")
        return super().form_valid(form)


# ──────────────────────────────────────────────
# Panel de administración web
# ──────────────────────────────────────────────
@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    from django.contrib.auth.models import User
    
    # Estadísticas
    total_posts = Post.objects.count()
    total_users = User.objects.count()
    recent_posts = Post.objects.select_related('autor').order_by('-fecha_creacion')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    context = {
        'total_posts': total_posts,
        'total_users': total_users,
        'recent_posts': recent_posts,
        'recent_users': recent_users,
    }
    
    return render(request, 'admin_panel.html', context)


# ──────────────────────────────────────────────
# Gestión de usuarios (solo admin)
# ──────────────────────────────────────────────
@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    from django.contrib.auth.models import User
    from django.core.paginator import Paginator
    
    users = User.objects.all().order_by('-date_joined')
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'user_list.html', {'page_obj': page_obj})

@user_passes_test(lambda u: u.is_superuser)
def user_toggle_status(request, user_id):
    from django.contrib.auth.models import User
    from django.shortcuts import get_object_or_404, redirect
    
    user = get_object_or_404(User, id=user_id)
    
    # No permitir desactivar al propio usuario admin
    if user == request.user:
        messages.error(request, "❌ No puedes desactivar tu propia cuenta.")
        return redirect('blog:user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = "activado" if user.is_active else "desactivado"
    messages.success(request, f"✅ Usuario {user.username} ha sido {status}.")
    
    return redirect('blog:user_list')

@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, user_id):
    from django.contrib.auth.models import User
    from django.shortcuts import get_object_or_404, redirect
    
    user = get_object_or_404(User, id=user_id)
    
    # No permitir eliminar al propio usuario admin
    if user == request.user:
        messages.error(request, "❌ No puedes eliminar tu propia cuenta.")
        return redirect('blog:user_list')
    
    # Eliminar todos los posts del usuario primero
    Post.objects.filter(autor=user).delete()
    
    username = user.username
    user.delete()
    
    messages.success(request, f"🗑️ Usuario {username} y todos sus posts han sido eliminados.")
    
    return redirect('blog:user_list')