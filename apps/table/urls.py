"""Urls for table app"""
from django.urls import path
from .views import (DasboardView,
                    TableListView,
                    TableView,
                    TableEditView,
                    TableObjectEditView,
                    TableObjectDeleteView,
                    ImportTableDataView,
                    ExportTableDataView
                    )


urlpatterns = [

    path('', DasboardView.as_view()),
    path('table/', TableListView.as_view()),
    path('table/<int:table_id>/', TableView.as_view()),
    path('table/add/', TableEditView.as_view()),
    path('table/<int:table_id>/edit/', TableEditView.as_view()),

    path('table/<int:table_id>/add/', TableObjectEditView.as_view()),
    path('table/<int:table_id>/<int:object_id>/edit/', TableObjectEditView.as_view()),
    path('table/<int:table_id>/<int:object_id>/delete/', TableObjectDeleteView.as_view()),

    path('table/<int:table_id>/import/', ImportTableDataView.as_view()),
    path('table/<int:table_id>/export/', ExportTableDataView.as_view())

]
