from rest_framework import serializers
from .models import AuditScore, News, Organization, CatalogItem, IconUpload, OverlayUpload, SurveyTemplate, Job, ImageUpload, Leaderboard, StreamData, Location
from .utils import ImageToBase64Converter
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        depth = 1  # Serialize one level of nested relationships


class CatalogItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogItem
        fields = '__all__'
        depth = 1  # Serialize one level of nested relationships


class IconUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = IconUpload
        fields = '__all__'
        depth = 1  # Serialize one level of nested relationships

class OverlayUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = OverlayUpload
        fields = '__all__'
        depth = 1  # Serialize one level of nested relationships

class SurveyTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyTemplate
        fields = '__all__'

class CatalogItemsSerializer(serializers.ModelSerializer):
    surveys = SurveyTemplateSerializer(many=True, read_only=True)

    class Meta:
        model = CatalogItem
        fields = '__all__'  # Include the 'surveys' field which represents related SurveyTemplate instances


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'  # Serialize all fields, you can also list fields explicitly if needed


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = '__all__'

# class HistorySerializer(serializers.ModelSerializer):
#     image_base64 = serializers.SerializerMethodField()

#     class Meta:
#         model = ImageUpload
#         fields = ['id', 'name', 'image', 'image_base64', 'uploaded_by', 'uploaded_at', 'is_inferred', 'subcategory', 'category', 'location']
#         depth = 1  # Adjust the depth level based on your model relationships

#     def get_image_base64(self, obj):
#         if obj.image:
#             image_convertor = ImageToBase64Converter(obj.image.path)
#             image_string = image_convertor.convert_image_to_base64()
#             return image_string
#         return None
    
class HistorySerializer(serializers.ModelSerializer):
    image_base64 = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()  # Field to fetch the location name

    class Meta:
        model = ImageUpload
        fields = ['id', 'name', 'uploaded_at', 'is_inferred', 'subcategory', 'category', 'location_name']
        depth = 1  # Adjust the depth level based on your model relationships

    def get_image_base64(self, obj):
        if obj.image:
            try:
                image_convertor = ImageToBase64Converter(obj.image.path)
                image_string = image_convertor.convert_image_to_base64()
                return image_string
            except Exception as e:
                return str(e)
        return None

    def get_location_name(self, obj):
        # This method returns the name of the location associated with the image upload
        return obj.location.name if obj.location else None
class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaderboard
        fields = '__all__'

class StreamDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamData
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'subtitle', 'content', 'image', 'publication_date', 'author']
        read_only_fields = ['id', 'publication_date']

class AuditScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditScore
        fields = '__all__' 