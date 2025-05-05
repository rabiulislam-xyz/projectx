from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from account.serializers import UserSerializer
from projectx.permissions import IsOwnAccount

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('=username', '=email', '=phone',
                     'first_name', 'last_name')

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (AllowAny,)

        elif self.action in ('update', 'partial_update', 'destroy'):
            self.permission_classes = (IsOwnAccount,)

        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get the authenticated user's details.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
