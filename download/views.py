from rest_framework import viewsets
from download.models import Download
from download.serializers import DownloadSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated

class DownloadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Download.objects.none()
    serializer_class = DownloadSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Download.objects.filter(
            created_by=self.request.user
        ).order_by('-pk')
    