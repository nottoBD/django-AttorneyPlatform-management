from django.conf.urls.static import static
from django.urls import path
from django.conf import settings

from .views import (PaymentHistoryView, CaseListView, CategoryPaymentsView, add_category,
                    PaymentHistoryPDFView, index_payments, delete_indexation, submit_payment_document, create_case,
                    pending_payments, add_juge_avocat, remove_juge, remove_avocat, create_draft_case, DraftCaseListView,
                    convert_draft_case, combine_drafts, add_child, delete_child, update_percentages)

app_name = 'payments'
urlpatterns = [
    path('add_category/', add_category, name='add_category'),
    path('payment-history/<uuid:case_id>/', PaymentHistoryView.as_view(), name='payment-history'),
    path('payment-history/<uuid:case_id>/<uuid:category_id>/', CategoryPaymentsView.as_view(), name='category-payments'),
    path('create_case/', create_case, name='create_case'),
    path('list_case/', CaseListView.as_view(), name='list_case'),
    path('cases/draft/', create_draft_case, name='create_draft_case'),
    path('list_draft/', DraftCaseListView.as_view(), name='list_draft_cases'),
    path('cases/convert_draft/<uuid:case_id>/', convert_draft_case, name='convert-draft-case'),
    path('cases/combine_drafts/', combine_drafts, name='combine_drafts'),
    path('download_pdf/<uuid:case_id>/', PaymentHistoryPDFView.as_view(), name='download_pdf'),
    path('pending-payments/<uuid:case_id>/', pending_payments, name='pending-payments'),
    path('add-payment/<uuid:case_id>/', submit_payment_document, name='add-payment'),
    path('index_payments/', index_payments, name='index_payments'),
    path('delete-indexation/<uuid:index_id>/', delete_indexation, name='delete_indexation'),
    path('add-judge-parent/<uuid:case_id>/', add_juge_avocat, name='add-juge-avocat'),
    path('remove-juge/<uuid:case_id>/<uuid:juge_id>/', remove_juge, name='remove-juge'),
    path('remove-avocat/<uuid:case_id>/<uuid:avocat_id>/', remove_avocat, name='remove-avocat'),
    path('cases/<uuid:case_id>/child/', add_child, name='child'),
    path('cases/<uuid:case_id>/delete_child/<uuid:child_id>/', delete_child, name='delete_child'),
    path('case/<uuid:case_id>/update_percentages/', update_percentages, name='update_percentages'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
