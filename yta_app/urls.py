from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AuditDataViewSet, CatalogItemViewSet, CatalogItemsViewSet, IconUploadViewSet, ImageUploadViewSet, JobViewSet, LeaderboardViewSet, LocationViewSet, NewsViewSet, OrganizationViewSet, OverlayUploadViewSet, StreamDataViewSet, UploadAuditDataView, UploadHistoryViewSet
from schema_graph.views import Schema

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'catalogitems', CatalogItemViewSet, basename='catalogitem-simple')
router.register(r'catalog-details', CatalogItemsViewSet, basename='catalogitem-detailed')
router.register(r'iconuploads', IconUploadViewSet, basename='iconupload')
router.register(r'overlay-uploads', OverlayUploadViewSet, basename='overlayupload')
router.register(r'imageuploads', ImageUploadViewSet, basename='imageupload')
router.register(r'upload-history', UploadHistoryViewSet, basename='upload-history')
router.register(r'leaderboards', LeaderboardViewSet, basename='leaderboard')
router.register(r'streamdata', StreamDataViewSet, basename='streamdata')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'audit-data', AuditDataViewSet, basename='audit-data')
router.register(r'news', NewsViewSet)

urlpatterns = [
    # Here you define the URL pattern for your UploadAuditDataView.
    path('upload-audit/', UploadAuditDataView.as_view(), name='upload-audit'),
    path('', include(router.urls)),
    path("schema/", Schema.as_view()),


]
