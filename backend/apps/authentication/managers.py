"""
Manager personalizado para el modelo User.
Usa teléfono en lugar de username.
"""

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Manager de usuarios. Reemplaza el comportamiento estándar
    de Django para usar phone como campo de identificación.
    """

    def create_user(
        self,
        phone: str,
        first_name: str,
        password: str | None = None,
        **extra_fields,
    ):
        """
        Crea y guarda un usuario con teléfono y nombre.
        Los clientes no usan contraseña.
        """
        if not phone:
            raise ValueError("El teléfono es obligatorio.")

        user = self.model(
            phone=phone,
            first_name=first_name,
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        phone: str,
        first_name: str,
        password: str,
        **extra_fields,
    ):
        """
        Crea y guarda un superusuario administrador.
        Usado por: python manage.py createsuperuser
        """
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            phone=phone,
            first_name=first_name,
            password=password,
            **extra_fields,
        )
