from django.urls import path
from about.views import NewsItemViewSet

urlpatterns = [
    path('news/', NewsItemViewSet.as_view({'get': 'list'})),
]
