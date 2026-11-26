from django.urls import path
from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cv/<int:pk>/download/", views.download_cv_pdf, name="download_cv_pdf"),
    path("matches/<int:pk>/", views.match_detail, name="match_detail"),
    path("history/", views.history, name="history"),
    path("profile/", views.cv_list, name="cv_list"),
    path("profile/upload/", views.cv_upload, name="cv_upload"),
    path("profile/enhanced/<int:pk>/", views.cv_detail, name="cv_detail"),
    path("profile/enhanced/<int:pk>/default/", views.enhanced_default, name="enhanced_default"),
    path("profile/enhanced/<int:pk>/delete/", views.enhanced_delete, name="enhanced_delete"),
    path("profile/originals/<int:pk>/enhance/", views.cv_enhance, name="cv_enhance"),
    path("profile/originals/<int:pk>/delete/", views.cv_delete, name="cv_delete"),
]
