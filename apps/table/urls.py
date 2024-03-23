"""Urls for table app"""
from django.urls import path
from .views import (DasboardView,
                    TableListView,
                    TableCreateView,
                    TableUpdateView,
                    TableObjectListView,
                    TableObjectCreateView,
                    TableObjectEditView,
                    TableObjectDeleteView,
                    RelatedTableObjectsListView,
                    ExportTableDataView, TableDeleteView)


urlpatterns = [
    path('', DasboardView.as_view()),
    path('table/', TableListView.as_view(), name="table-list"),

    path('table/add/', TableCreateView.as_view(), name='table-add'),
    path('table/<int:table_id>/edit/', TableUpdateView.as_view(), name='table-edit'),
    path('table/<int:table_id>/delete/', TableDeleteView.as_view(), name='table-delete'),
    path('table/<int:table_id>/list/', TableObjectListView.as_view(), name="object-list"),

    path('table/<int:table_id>/add/', TableObjectCreateView.as_view(), name="object-add"),
    path('table/<int:table_id>/<int:object_id>/related/<int:related_table_id>', RelatedTableObjectsListView.as_view(),
         name="related-list"),
    path('table/<int:table_id>/<int:object_id>/edit/', TableObjectEditView.as_view(),
                                                       name="object-edit"),
    path('table/<int:table_id>/<int:object_id>/delete/', TableObjectDeleteView.as_view(), 
                                                         name="object-delete"),
    path('table/<int:table_id>/export/', ExportTableDataView.as_view())

]
