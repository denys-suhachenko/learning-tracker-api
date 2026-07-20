from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from strawberry.django.views import GraphQLView

from config.schema import schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('learning.urls')),
    path('api/auth/', include('users.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path('graphql/', GraphQLView.as_view(schema=schema)),
]
