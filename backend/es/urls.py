from django.urls import path
from es.views import ForwardSearchView

urlpatterns = [
    path('<str:corpus>/_search', ForwardSearchView.as_view()),
]
