from rest_framework import viewsets

from about.serializers import NewsItemSerializer
from about.models import NewsItem

class NewsItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsItem.objects.all()
    serializer_class = NewsItemSerializer
