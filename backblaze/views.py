from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from backblaze.models import FileModel
from backblaze.utils.b2_utils import converter_to_webP, delete_file_from_backblaze
from backblaze.utils.validation import image_validation
from rest_framework.validators import ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

# Create your views here.


class UploadImage(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = FileModel.objects.all()

    def create(self, request):
        uploaded_files = request.FILES.getlist("image")
        response_data = []

        for file_obj in uploaded_files:
            try:
                # Validate image
                image_validation(file_obj)

                # Convert image to webp
                webp_image_name, webp_image_id, image_url = converter_to_webP(file_obj)

                file_model = FileModel(
                    id=webp_image_id,
                    name=webp_image_name,
                    url=image_url,
                    category="image",
                )
                file_model.save()

                response_data.append(
                    {
                        "message": "Зображення успішно завантажено",
                        "image_url": image_url,
                        "image_id": webp_image_id,
                        "image_name": webp_image_name,
                    }
                )

            except ValidationError as e:
                response_data.append({"error": str(e)})

        return Response(response_data, status=status.HTTP_200_OK)
