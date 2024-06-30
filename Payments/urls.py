from django.conf.urls.static import static
from django.urls import path
from django.conf import settings

from . import views
from .views import PaymentHistoryView, MagistrateFolderListView, FolderPaymentHistoryView, \
    submit_payment_document_lawyer, PaymentDeleteView, CategoryPaymentsView

app_name = 'Payments'
urlpatterns = [
    path('parent-add-payment/', views.submit_payment_document, name='parent-add-payment'),
    path('parent-payment-history/', PaymentHistoryView.as_view(), name='parent-payment-history'),
    path('parent-payment-history/category/<int:category_id>/', CategoryPaymentsView.as_view(), name='category-payments'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('list_folder/', MagistrateFolderListView.as_view(), name='list_folder'),
    path('magistrate-/<int:folder_id>/', FolderPaymentHistoryView.as_view(),name='folder_payment_history'),
    path('lawyer-add-payment/<int:folder_id>/', submit_payment_document_lawyer, name='add-doc-magistrate'),
    path('delete-payment/<int:pk>/', PaymentDeleteView.as_view(), name='delete_payment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
