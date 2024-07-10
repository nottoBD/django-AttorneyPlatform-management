from django.conf.urls.static import static
from django.urls import path
from django.conf import settings

from . import views
from .views import PaymentHistoryView, FolderListView, MagistrateFolderPaymentHistoryView, \
    submit_payment_document_lawyer, PaymentDeleteView, CategoryPaymentsView, add_category, \
    MagistrateCategoryPaymentsView, PaymentHistoryPDFView

app_name = 'Payments'
urlpatterns = [
    path('parent-add-payment/', views.submit_payment_document, name='parent-add-payment'),
    path('add_category/', add_category, name='add_category'),
    path('parent-payment-history/', PaymentHistoryView.as_view(), name='parent-payment-history'),
    path('parent-payment-history/category/<int:category_id>/', CategoryPaymentsView.as_view(), name='category-payments'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('list_folder/', FolderListView.as_view(), name='list_folder'),
    path('magistrate-/<int:folder_id>/', MagistrateFolderPaymentHistoryView.as_view(), name='magistrate_folder_payment_history'),
    path('magistrate-payment-history/folder/<int:folder_id>/category/<int:category_id>/', MagistrateCategoryPaymentsView.as_view(), name='magistrate-category-payments'),
    path('pending-payments/<int:folder_id>/', views.pending_payments, name='pending-payments'),
    path('lawyer-add-payment/<int:folder_id>/', submit_payment_document_lawyer, name='lawyer-add-payment'),
    path('delete-payment/<int:pk>/', PaymentDeleteView.as_view(), name='delete_payment'),
    path('download_pdf/', PaymentHistoryPDFView.as_view(), name='download_pdf'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
