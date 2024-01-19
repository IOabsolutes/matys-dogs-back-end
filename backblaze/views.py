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
from about.models import AboutModel as About
from backblaze.serializer import FileSerializer
# Create your views here.


class UploadImage(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = FileSerializer

    def get_queryset(self):
        about_instanse = About.objects.first()
        if about_instanse:
            return about_instanse.images.all()
        else:
            return FileModel.objects.none()

    # get images

    def list(self, request):
        queryset = self.get_queryset()
        serializer = FileSerializer(queryset, many=True)
        return Response(serializer.data)

    # upload image
    def create(self, request):
        uploaded_files = request.FILES.getlist('image')
        response_data = []

        for file_obj in uploaded_files:
            try:
                # Validate image
                image_validation(file_obj)

                # Convert image to webp
                webp_image_name, webp_image_id, bucket_name, size = converter_to_webP(
                    file_obj)

                # Save image to database
                image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
                file_model = FileModel(id=webp_image_id, name=webp_image_name,
                                       url=image_url, category='image')
                file_model.save()

                response_data.append({
                    'message': 'Зображення успішно завантажено',
                    'image_url': image_url,
                    'image_id': webp_image_id,
                    'image_name': webp_image_name,
                    'size': size
                })

            except ValidationError as e:
                response_data.append({'error': str(e)})

        return Response(response_data, status=status.HTTP_200_OK if response_data else status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, file_id):
        try:
            # Get file from database
            file_model = FileModel.objects.get(id=file_id)
            if not file_model:
                delete_file_from_backblaze(file_id)
                return Response({'message': 'Файл успішно видалено'}, status=status.HTTP_200_OK)

            # Delete file from Backblaze
            delted_file = delete_file_from_backblaze(file_id)
            if not delete_file:
                file_model.delete()
                return Response({'message': 'Файл успішно видалено'}, status=status.HTTP_200_OK)

            # Delete file from database
            if delted_file:
                file_model.delete()
                return Response({'message': 'Файл успішно видалено', 'file_name': delted_file.file_name, 'file_id': delted_file.file_id}, status=status.HTTP_200_OK)
        except FileModel.DoesNotExist:
            return Response({'error': 'Файл не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Неочікувана помилка: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def upload_image(request):
#     uploaded_files = request.FILES.getlist('image')
#     response_data = []

#     for file_obj in uploaded_files:
#         try:
#             # Validate image
#             image_validation(file_obj)

#             # Convert image to webp
#             webp_image_name, webp_image_id, bucket_name, size = converter_to_webP(
#                 file_obj)

#             # Save image to database
#             image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
#             file_model = FileModel(id=webp_image_id, name=webp_image_name,
#                                    url=image_url, category='image')
#             file_model.save()

#             response_data.append({
#                 'message': 'Зображення успішно завантажено',
#                 'image_url': image_url,
#                 'image_id': webp_image_id,
#                 'image_name': webp_image_name,
#                 'size': size
#             })

#         except ValidationError as e:
#             response_data.append({'error': str(e)})

#     return Response(response_data, status=status.HTTP_200_OK if response_data else status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request, file_id):
    try:
        try:
            # Get file from database
            file_model = FileModel.objects.get(id=file_id)
            if not file_model:
                delete_file_from_backblaze(file_id)
                return Response({'message': 'Файл успішно видалено'}, status=status.HTTP_200_OK)

            # Delete file from Backblaze
            delted_file = delete_file_from_backblaze(file_id)
            if not delete_file:
                file_model.delete()
                return Response({'message': 'Файл успішно видалено'}, status=status.HTTP_200_OK)

            # Delete file from database
            if delted_file:
                file_model.delete()
                return Response({'message': 'Файл успішно видалено', 'file_name': delted_file.file_name, 'file_id': delted_file.file_id}, status=status.HTTP_200_OK)
        except FileModel.DoesNotExist:
            return Response({'error': 'Файл не знайдено'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Неочікувана помилка: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def upload_document(request):
#     try:
#         file_obj = request.FILES['document']
#         # Validate document
#         document_validation(file_obj)
#         # upload document
#         doc_name, doc_id, bucket_name = document_simplify_upd(file_obj)
#         # Save document to database
#         document_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{doc_name}'
#         file_model = FileModel(id=doc_id,
#                                name=doc_name, url=document_url, category='document')
#         file_model.save()
#         return Response({'message': 'Документ успішно завантажений', 'document_url': document_url, 'document_id': doc_id, 'document_name': doc_name}, status=status.HTTP_200_OK)
#     except ValidationError as e:
#         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
