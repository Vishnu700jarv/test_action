from rest_framework import serializers
from .models import News, Organization, CatalogItem, IconUpload, OverlayUpload, SurveyTemplate, Job, ImageUpload, Leaderboard, StreamData, Location

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