from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    contenido = models.TextField(verbose_name="Contenido")
    autor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Autor"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.pk})