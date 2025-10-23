"""
PokeAPI URL Configuration (versión PRO)
---------------------------------------
Centraliza y documenta todas las rutas principales del proyecto Pokémon.

📌 Rutas principales:
  - /admin/         → Panel administrativo de Django
  - /api/auth/      → Módulo de autenticación JWT (Login, Registro)
  - /api/pokemon/   → Endpoints de Pokémon, Tipos y Movimientos
  - /api/health/    → Verificación del estado del backend
  - /api/swagger/   → Documentación interactiva (Swagger UI)
  - /api/redoc/     → Documentación alternativa (Redoc UI)

Autor: Equipo Pokémon Project
Fecha: 2025-10-23
"""

# ============================================================
# 🧱 IMPORTS PRINCIPALES
# ============================================================
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ============================================================
# 🩺 HEALTH CHECK (para monitoreo rápido)
# ============================================================
def health_check(request):
    """
    Devuelve una respuesta rápida para confirmar que el backend está activo.
    Ideal para monitoreo, despliegues o integración con frontend.
    """
    return JsonResponse({
        "status": "ok",
        "service": "PokeAPI Backend",
        "version": "1.0.0",
        "framework": "Django REST Framework",
        "author": "Equipo Pokémon Project",
    })


# ============================================================
# 📘 CONFIGURACIÓN SWAGGER Y REDOC
# ============================================================
schema_view = get_schema_view(
    openapi.Info(
        title="PokeAPI - Documentación REST",
        default_version="v1",
        description=(
            "API REST construida con Django REST Framework.\n\n"
            "Incluye los módulos:\n"
            " - 🔐 Autenticación con JWT (Login y Registro)\n"
            " - ⚔️ Pokémon (CRUD, captura, tipos y movimientos)\n"
            " - 🩺 Health Check para monitoreo\n\n"
            "👉 Compatible con frontend React y Battle System"
        ),
        contact=openapi.Contact(email="soporte@pokeapi.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


# ============================================================
# 🧭 DEFINICIÓN DE RUTAS PRINCIPALES
# ============================================================
urlpatterns = [
    # 🧩 Panel de administración
    path("admin/", admin.site.urls),

    # 🔐 Autenticación (JWT o clásica)
    path("api/auth/", include("authentication.urls")),

    # ⚔️ Módulo Pokémon (Pokémon, Tipos y Movimientos)
    path("api/pokemon/", include("pokemon.urls")),

    # 🩺 Health check del backend
    path("api/health/", health_check, name="api-health"),

    # 📘 Swagger (interactivo) y Redoc (lectura)
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]


# ============================================================
# 🖥️ MENSAJE EN CONSOLA AL INICIAR EL SERVIDOR
# ============================================================
def _startup_banner():
    """Imprime en consola las rutas principales cargadas correctamente."""
    print("\n" + "=" * 60)
    print("✅ PokeAPI cargada correctamente")
    print("🌐  Endpoints principales:")
    print("   • Admin:          /admin/")
    print("   • Auth:           /api/auth/")
    print("   • Pokémon:        /api/pokemon/")
    print("   • Health:         /api/health/")
    print("   • Swagger UI:     /api/swagger/")
    print("   • Redoc UI:       /api/redoc/")
    print("=" * 60 + "\n")


_startup_banner()
