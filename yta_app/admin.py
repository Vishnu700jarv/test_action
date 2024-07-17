from django.contrib import admin
from .models import AuditScore, News, Organization, CatalogItem, IconUpload, OverlayUpload, SurveyTemplate, Job, ImageUpload, Leaderboard, StreamData, Location

admin.site.register(Organization)
admin.site.register(CatalogItem)
admin.site.register(IconUpload)
admin.site.register(OverlayUpload)
admin.site.register(SurveyTemplate)
admin.site.register(Job)
admin.site.register(ImageUpload)
admin.site.register(Leaderboard)
admin.site.register(StreamData)
admin.site.register(Location)
admin.site.register(News)
admin.site.register(AuditScore) 