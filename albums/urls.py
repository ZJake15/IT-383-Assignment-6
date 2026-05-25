from django.urls import path
from . import views

urlpatterns = [
    # Album CRUD
    path('', views.AlbumListView.as_view(), name='album_list'),
    path('album/create/', views.AlbumCreateView.as_view(), name='album_create'),
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
    path('album/<int:pk>/update/', views.AlbumUpdateView.as_view(), name='album_update'),
    path('album/<int:pk>/delete/', views.AlbumDeleteView.as_view(), name='album_delete'),
    
    # Photo actions inside album
    path('album/<int:album_pk>/photo/upload/', views.PhotoCreateView.as_view(), name='photo_create'),
    path('photo/<int:pk>/update/', views.PhotoUpdateView.as_view(), name='photo_update'),
    path('photo/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
    
    # Admin Control Panel
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Custom styled auth routes
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
]
