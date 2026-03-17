#
from django.urls import path
from . import views

app_name = "users_app"

urlpatterns = [
    path(
        'register/',
        views.UserRegisterView.as_view(),
        name='user-register',
    ),
    path(
        'login/',
        views.LoginUser.as_view(),
        name='user-login',
    ),
    path(
        'logout/',
        views.LogoutView.as_view(),
        name='user-logout',
    ),
    path(
        'update/',
        views.UpdatePasswordView.as_view(),
        name='user-update',
    ),
    path(
        'users/lista/',
        views.UserListView.as_view(),
        name='user-lista',
    ),
    #exportar pdf y excel
    path(
        'users/reporte/excel/',
        views.UserReporteExcelView.as_view(),
        name='user-reporte-excel',
    ),
    path(
        'users/reporte/pdf/',
        views.UserReportePDFView.as_view(),
        name='user-reporte-pdf',
    ),

    path(
        'users/<int:pk>/editar/',
        views.UserUpdateView.as_view(),
        name='user-editar',
    ),

]
