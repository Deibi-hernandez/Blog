from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # ── Listado y detalle ──────────────────────────────
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),

    # ── CRUD ──────────────────────────────────────────
    path("post/nuevo/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/editar/", views.PostUpdateView.as_view(), name="post_update"),
    path("post/<int:pk>/eliminar/", views.PostDeleteView.as_view(), name="post_delete"),

    # ── Autenticación ─────────────────────────────────
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("registro/", views.CustomUserCreateView.as_view(), name="registro"),
    
    # ── Panel de administración ───────────────────────
    path("panel/", views.admin_panel, name="admin_panel"),
    path("panel/usuarios/", views.user_list, name="user_list"),
    path("panel/usuarios/<int:user_id>/toggle/", views.user_toggle_status, name="user_toggle"),
    path("panel/usuarios/<int:user_id>/eliminar/", views.user_delete, name="user_delete"),
]