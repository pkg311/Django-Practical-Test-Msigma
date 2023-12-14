from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    # User authentication URLs
    path('register/', views.UserRegistrationView.as_view(), name='register'),  # URL for user registration
    path('login/', views.UserLoginView.as_view(), name='login'),  # URL for user login
    path('logout/', views.UserLogoutView.as_view(), name='logout'),  # URL for user logout

    # Post-related URLs
    path('search_users/', views.search_users, name='search_users'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),  # URL for creating a post
    path('', views.PostListView.as_view(), name='post_list'),  # URL for listing all posts
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),  # URL for a specific post detail
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='update_post'),  # URL for updating a post
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),  # URL for deleting a post

    # Django admin URL
    # path('admin/', admin.site.urls),  # URL for Django admin
]


# Serving static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
