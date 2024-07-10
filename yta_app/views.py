from django.utils import timezone
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from django.core.files.base import ContentFile
import base64
import uuid
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ytauser.models import CustomUser
from .models import Job, News, Organization, CatalogItem, IconUpload, ImageUpload, Leaderboard, OverlayUpload, StreamData, Location, SurveyTemplate
from .serializers import CatalogItemsSerializer, JobSerializer, NewsSerializer,OverlayUploadSerializer, OrganizationSerializer, CatalogItemSerializer, IconUploadSerializer, ImageUploadSerializer, LeaderboardSerializer, StreamDataSerializer, LocationSerializer
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from .utils import ImageToBase64Converter


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the 'created_by' field to the logged-in user
        serializer.save(created_by=self.request.user)

class CatalogItemViewSet(viewsets.ModelViewSet):
    queryset = CatalogItem.objects.all()
    serializer_class = CatalogItemSerializer
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class IconUploadViewSet(viewsets.ModelViewSet):
    queryset = IconUpload.objects.all()
    serializer_class = IconUploadSerializer
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

class OverlayUploadViewSet(viewsets.ModelViewSet):
    queryset = OverlayUpload.objects.all()
    serializer_class = OverlayUploadSerializer
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class CatalogItemsViewSet(viewsets.ModelViewSet):
    queryset = CatalogItem.objects.all().prefetch_related('surveys')
    serializer_class = CatalogItemsSerializer
    permission_classes = [IsAuthenticated]



class ImageUploadViewSet(viewsets.ModelViewSet):
    queryset = ImageUpload.objects.all()
    serializer_class = ImageUploadSerializer

class LeaderboardViewSet(viewsets.ModelViewSet):
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
    permission_classes = [IsAuthenticated]


class StreamDataViewSet(viewsets.ModelViewSet):
    queryset = StreamData.objects.all()
    serializer_class = StreamDataSerializer
    permission_classes = [IsAuthenticated]


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        queryset = Location.objects.all()
        # Get the search parameter from the request
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            # Filter queryset based on search parameter
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(address__icontains=search_query))
        
        return queryset

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        queryset = super().get_queryset()  # Start with the base queryset
        search_query = self.request.query_params.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
                # You can add more fields to filter upon depending on your model structure
            )

        return queryset


class AuditDataViewSet(viewsets.ViewSet):
    def list(self, request):
        # Fetch all catalog items
        catalog_items = CatalogItem.objects.all()

        # Dictionary to group subcategories under the same category
        categories = {}

        # Iterate over each catalog item to structure and group the nested data
        for item in catalog_items:
            # Fetch related surveys through the foreign key relationship
            related_surveys = SurveyTemplate.objects.filter(catalog_id=item.id)

            # Check if the category already exists in the dictionary
            if item.category_name not in categories:
                categories[item.category_name] = {
                    "category_name": item.category_name,
                    "sub_categories": []
                }

            # List to hold surveys for the current sub_category
            surveys_list = []
            for survey in related_surveys:
                # Safely access survey_template data
                # questions = []
                # if isinstance(survey.survey_template, dict) and 'questions' in survey.survey_template:
                #     # questions = [{
                #     #     "id": question.get('id', None),
                #     #     "text": question.get('text', ''),
                #     #     "type": question.get('type', '')
                #     # } for question in survey.survey_template['questions']]

                surveys = {
                    "survey_date": survey.survey_date.strftime('%Y-%m-%d'),
                    "description": survey.description,
                    "survey_template": {
                        "questions": survey.survey_template
                    }
                }
                surveys_list.append(surveys)
            # icon_converter = ImageToBase64Converter(item.sub_category_icon.icon_file.path)
            # icon = icon_converter.convert_image_to_base64()
            # print("*"*100)
            # print(item.overlay)
            # print("*"*100)
            # overlay_converter = ImageToBase64Converter(item.overlay.overlay_file.path)
            # overlay = overlay_converter.convert_image_to_base64()
            # Check if item.sub_category_icon and item.sub_category_icon.icon_file are not None
            if item.sub_category_icon is not None and item.sub_category_icon.icon_file is not None:
                icon_converter = ImageToBase64Converter(item.sub_category_icon.icon_file.path)
                icon = icon_converter.convert_image_to_base64()
            else:
                icon_converter = None
                icon = None  # or handle it accordingly
                print("Sub-category icon or icon file is None")

            print("*" * 100)
            print(item.overlay)
            print("*" * 100)

            # Check if item.overlay and item.overlay.overlay_file are not None
            if item.overlay is not None and item.overlay.overlay_file is not None:
                overlay_converter = ImageToBase64Converter(item.overlay.overlay_file.path)
                overlay = overlay_converter.convert_image_to_base64()
            else:
                overlay_converter = None
                overlay = None  # or handle it accordingly
                print("Overlay or overlay file is None")

            # You can continue with further processing, handling the case where icon or overlay might be None

            # Append the subcategory with its surveys to the category in the dictionary
            categories[item.category_name]["sub_categories"].append({
                "sub_category_name": item.sub_category_name,
                "image": '',  # Placeholder or logic for images
                "classname":item.classname,
                "success_message":item.success_message,
                "error_message":item.error_message,
                "detection_info":item.detection_info,
                "help_text":item.help_text,
                "reserved1":item.reserved1,
                "reserved2":item.reserved2,  
                "icon": icon,
                "overlay": overlay,
                "surveys": surveys_list
            })

        # Convert the categories dictionary to a list for the response
        audit_data_list = list(categories.values())

        # Structure the final JSON response
        response = {
            "auditLocationDetails": {
                "auditor": "Specify Auditor Name",
                "yourLocation": "Specify Location",
                "latitude": "Specify Latitude",
                "longitude": "Specify Longitude",
                "nameOfThePlace": "Specify Place Name",
                "typeOfThePlace": "Specify Place Type",
                "additionalComments": "Any Additional Comments"
            },
            "auditData": audit_data_list
        }

        return Response(response, status=status.HTTP_200_OK)



class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UploadAuditDataView(APIView):
    # permission_classes = [IsAuthenticated]

    def parse_audit_data(self, audit_data):
        category_names = set()
        sub_categories_by_category = []

        for item in audit_data:
            category_name = item['category_name']
            category_names.add(category_name)
            sub_category_list = []

            for sub_cat in item['sub_categories']:
                sub_category_list.append(sub_cat['sub_category_name'])

            # Check if the category already exists in the list and update it
            existing_category = next((sc for sc in sub_categories_by_category if sc['category'] == category_name), None)
            if existing_category:
                existing_category['subcategories'].extend(sub_category_list)  # Add new subcategories
                existing_category['subcategories'] = list(set(existing_category['subcategories']))  # Remove duplicates
            else:
                sub_categories_by_category.append({
                    'category': category_name,
                    'subcategories': sub_category_list
                })

        return {
            'categories': list(category_names),
            'subcategories': sub_categories_by_category
        }

    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)

       

        location_data = data['auditLocationDetails']
        audit_data = data['auditData']

        # Create Location instance
        location_instance = Location(
            name=location_data['nameOfThePlace'],
            address=location_data['yourLocation'],
            location_type=location_data['typeOfThePlace'],
            latitude=location_data['latitude'],
            longitude=location_data['longitude']
        )
        
        # location_instance.save()

        categories = self.parse_audit_data(audit_data)
        
        job_instance = Job(
                location=location_instance.name,
                category_list=', '.join(categories['categories']),
                categories=categories['subcategories'],
                job_name=location_instance.name,
                job_description=location_data['additionalComments'],
                assigned_person=None,  # Assuming no one is assigned yet
                # created_by=CustomUser.objects.get(mobile=request.user.mobile),
                end_date=timezone.now() + timezone.timedelta(days=30),  # Setting a future end date
                organization=Organization.objects.first(),
                status='Accepted'
            )
        # job_instance.save()

        # Handle each job and its sub-categories
        for audit_item in audit_data:
            category_name =audit_item["category_name"]
            # Iterate over sub-categories, which include image and survey data
            for sub_cat in audit_item['sub_categories']:
                # Handling the image upload
                image_data = sub_cat['image']
                print("*"*100)
                print(sub_cat.get("surveys"))
                print("*"*100)
                if image_data:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    image_file = ContentFile(base64.b64decode(imgstr), name=f"{uuid.uuid4()}.{ext}")

                    image_upload_instance = ImageUpload(
                        name=category_name+"_"+sub_cat['sub_category_name'],
                        description=sub_cat.get('description', ''),  # Defaulting to empty string if not present
                        image=image_file,  # Ensure this is properly handled and created from uploaded image data
                        uploaded_by=request.user,  # Assuming the user is authenticated
                        category=category_name,  # Default category if not provided
                        subcategory= sub_cat.get('sub_category_name'),
                        location=location_instance,  # Associating with a location
                        jobno=job_instance,  # Associating with a job
                        survey=sub_cat.get('surveys', [])  # Assuming survey data is in a suitable format
                    )
                    # image_upload_instance.save()
                    # image_upload_instance.save()


        return JsonResponse({'status': 'success', 'message': 'Data uploaded successfully'})