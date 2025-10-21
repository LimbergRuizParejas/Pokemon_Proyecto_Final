from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.movimiento_viewset import MovimientoViewSet
from .api.tipo_viewset import TipoViewSet

router = DefaultRouter()
router.register(r'movimientos', MovimientoViewSet, basename='movimiento')
router.register(r'tipos', TipoViewSet, basename='tipo')

urlpatterns = [
    path('', include(router.urls)),
]