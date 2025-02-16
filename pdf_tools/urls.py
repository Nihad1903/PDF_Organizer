from django.urls import path
from . import views

urlpatterns = [
    path('', views.choicePage, name='choice_page'),
    path('merge/', views.mergePdfs, name='merge_pdfs'),
    path('split/', views.splitPdfs, name='split_pdfs'),
    path('image-to-pdf', views.imageToPdf, name='image_to_pdf'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
]