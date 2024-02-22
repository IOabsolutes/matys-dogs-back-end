from rest_framework import mixins, status, response, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.models import IsApprovedUser
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from .models import CallbackForm
from .serializer import UserCallBack, Notice, NoticeUpdateSerializer

# Create your views here.


class CallBackPost(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    A viewset for creating callback posts from users. This viewset allows any user to submit
    callback requests with their name, phone number, optional comment, and the ID of the dog
    they are interested in.
    """

    permission_classes = [AllowAny]
    queryset = CallbackForm
    serializer_class = UserCallBack

    @extend_schema(
        summary="Update notification",
        description="Update notification status",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "comment": {"type": "string"},
                    "id_dog": {"type": "integer"},
                },
                "required": ["name", "phone_number", "id_dog"],
            }
        },
        responses={200: Notice, 400: "Bad request", 500: "Internal server error"},
    )
    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new callback request. Validates the request data and saves
        the new callback form if valid. Returns the created callback form data on success.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


class NotificationAdmin(
    mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """
    A viewset for admin users to list and update notifications. Access is restricted to authenticated
    and approved users only. Supports listing all notifications and updating the status of individual notifications.
    """

    permission_classes = [IsAuthenticated, IsApprovedUser]
    queryset = CallbackForm.objects.all()
    serializer_class = Notice

    @extend_schema(
        summary="Get notification list",
        description="Get notification list",
        responses={200: Notice},
    )
    def list(self, request, *args, **kwargs):
        """
        Lists all notifications. This method is accessible only by authenticated and approved users.
        Returns a list of all callback form submissions.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Update notification",
        description="Update notification status",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "boolean",
                    },
                    "processing": {
                        "type": "boolean",
                    },
                    "is_read": {
                        "type": "boolean",
                    },
                },
            }
        },
        responses={
            200: Notice,
            404: "Not found",
            500: "Internal server error",
        },
    )
    def update(self, request, pk, *args, **kwargs):
        """
        Updates the status of a notification identified by its primary key. Validates the request data
        and applies the updates if valid. Returns the updated notification data on success.
        """
        try:
            instance = CallbackForm.objects.get(pk=pk)
            serializer = NoticeUpdateSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except CallbackForm.DoesNotExist:
            return response.Response(
                {"message": "Помилка - не знайдено"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return response.Response(
                {"message": f"Помилка {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
