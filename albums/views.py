from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Category, Tag, Album, Photo, AuditLog

# -------------------------------------------------------------
# RBAC Helper Functions
# -------------------------------------------------------------

def is_album_admin(user):
    """
    Checks if a user has Administrator privileges.
    """
    if not user.is_authenticated:
        return False
    return (
        user.is_superuser or 
        user.is_staff or 
        user.groups.filter(name='Album Administrators').exists()
    )

def get_client_ip(request):
    """
    Retrieves the IP address of the client request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# -------------------------------------------------------------
# Security & Access Mixins
# -------------------------------------------------------------

class AlbumReadRequiredMixin:
    """
    Mixin that ensures the user has permission to read the album.
    An album is readable if it is public, if the user owns it, or if the user is an admin.
    """
    def dispatch(self, request, *args, **kwargs):
        album = get_object_or_404(Album, pk=self.kwargs.get('pk') or self.kwargs.get('album_pk'))
        
        # Access control logic
        if album.is_private:
            if not request.user.is_authenticated:
                AuditLog.objects.create(
                    user=None,
                    action="UNAUTHORIZED_ACCESS_ATTEMPT",
                    details=f"Anonymous visitor attempted to view private album: '{album.title}' (ID {album.id})",
                    ip_address=get_client_ip(request)
                )
                messages.error(request, "This album is private. Please login with authorized credentials.")
                return redirect('login')
                
            if album.owner != request.user and not is_album_admin(request.user):
                AuditLog.objects.create(
                    user=request.user,
                    action="UNAUTHORIZED_ACCESS_ATTEMPT",
                    details=f"User '{request.user.username}' attempted to view private album: '{album.title}' (Owner: '{album.owner.username}')",
                    ip_address=get_client_ip(request)
                )
                messages.error(request, "You are not authorized to view this private album.")
                return redirect('album_list')
                
        return super().dispatch(request, *args, **kwargs)


class AlbumWriteRequiredMixin:
    """
    Mixin that ensures the user has permission to modify the album or upload photos.
    Only the owner or an admin can modify an album or upload to it.
    """
    def dispatch(self, request, *args, **kwargs):
        album = get_object_or_404(Album, pk=self.kwargs.get('pk') or self.kwargs.get('album_pk'))
        
        if not request.user.is_authenticated:
            messages.error(request, "Authentication is required to modify albums.")
            return redirect('login')
            
        if album.owner != request.user and not is_album_admin(request.user):
            AuditLog.objects.create(
                user=request.user,
                action="UNAUTHORIZED_MODIFY_ATTEMPT",
                details=f"User '{request.user.username}' attempted to modify album: '{album.title}' (Owner: '{album.owner.username}')",
                ip_address=get_client_ip(request)
            )
            messages.error(request, "You are not authorized to make changes to this album.")
            return redirect('album_detail', pk=album.id)
            
        return super().dispatch(request, *args, **kwargs)


# -------------------------------------------------------------
# Class-Based Views (CBVs)
# -------------------------------------------------------------

class AlbumListView(ListView):
    """
    Displays public albums and the user's own private albums.
    Supports search filtering, category filtering, and owner filtering.
    """
    model = Album
    template_name = 'albums/album_list.html'
    context_object_name = 'albums'
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user
        
        # Base logic: Album must be public, OR owned by the user, OR user must be an administrator
        if is_album_admin(user):
            queryset = Album.objects.all()
        elif user.is_authenticated:
            queryset = Album.objects.filter(Q(is_private=False) | Q(owner=user))
        else:
            queryset = Album.objects.filter(is_private=False)
            
        # 1. Search Query (title, description, tags, or owner)
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | 
                Q(description__icontains=q) |
                Q(owner__username__icontains=q) |
                Q(photos__tags__name__icontains=q)
            ).distinct()
            
        # 2. Category Filter
        cat_slug = self.request.GET.get('category', '').strip()
        if cat_slug:
            queryset = queryset.filter(category__slug=cat_slug)
            
        return queryset.select_related('owner', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        # Dynamic premium stats to display on top dashboard
        user = self.request.user
        if user.is_authenticated:
            context['total_albums'] = Album.objects.filter(owner=user).count() if not is_album_admin(user) else Album.objects.count()
            context['total_photos'] = Photo.objects.filter(album__owner=user).count() if not is_album_admin(user) else Photo.objects.count()
        else:
            context['total_albums'] = Album.objects.filter(is_private=False).count()
            context['total_photos'] = Photo.objects.filter(album__is_private=False).count()
            
        context['is_admin'] = is_album_admin(user)
        return context


class AlbumDetailView(AlbumReadRequiredMixin, DetailView):
    """
    Displays the photos inside an album.
    """
    model = Album
    template_name = 'albums/album_detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.all().prefetch_related('tags')
        
        # Determine edit permissions
        user = self.request.user
        context['can_modify'] = user.is_authenticated and (self.object.owner == user or is_album_admin(user))
        context['is_admin'] = is_album_admin(user)
        
        # Pass tags for upload form
        context['available_tags'] = Tag.objects.all()
        return context


class AlbumCreateView(LoginRequiredMixin, CreateView):
    """
    Handles creating a new Album.
    """
    model = Album
    template_name = 'albums/album_form.html'
    fields = ['title', 'description', 'category', 'is_private']
    success_url = reverse_lazy('album_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create Dynamic Album"
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        
        # Log action for audit logs
        AuditLog.objects.create(
            user=self.request.user,
            action="ALBUM_CREATE",
            details=f"Created album: '{self.object.title}' (ID {self.object.id}, Category: {self.object.category}, Private: {self.object.is_private})",
            ip_address=get_client_ip(self.request)
        )
        messages.success(self.request, f"Album '{self.object.title}' was created successfully!")
        return response


class AlbumUpdateView(LoginRequiredMixin, AlbumWriteRequiredMixin, UpdateView):
    """
    Handles modifying an Album.
    """
    model = Album
    template_name = 'albums/album_form.html'
    fields = ['title', 'description', 'category', 'is_private']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Edit Album: {self.object.title}"
        return context

    def get_success_url(self):
        return reverse('album_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log action for audit logs
        AuditLog.objects.create(
            user=self.request.user,
            action="ALBUM_UPDATE",
            details=f"Updated album: '{self.object.title}' (ID {self.object.id}, Private: {self.object.is_private})",
            ip_address=get_client_ip(self.request)
        )
        messages.success(self.request, f"Album '{self.object.title}' was updated successfully!")
        return response


class AlbumDeleteView(LoginRequiredMixin, AlbumWriteRequiredMixin, DeleteView):
    """
    Handles deleting an Album and all its photos.
    """
    model = Album
    template_name = 'albums/album_confirm_delete.html'
    success_url = reverse_lazy('album_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        album_title = self.object.title
        album_id = self.object.id
        
        response = super().delete(request, *args, **kwargs)
        
        # Log action for audit logs
        AuditLog.objects.create(
            user=request.user,
            action="ALBUM_DELETE",
            details=f"Deleted album: '{album_title}' (ID {album_id})",
            ip_address=get_client_ip(request)
        )
        messages.success(request, f"Album '{album_title}' and all its photos were deleted.")
        return response


# -------------------------------------------------------------
# Photo CBVs
# -------------------------------------------------------------

class PhotoCreateView(LoginRequiredMixin, AlbumWriteRequiredMixin, CreateView):
    """
    Handles uploading a Photo into a specific Album.
    """
    model = Photo
    fields = ['title', 'description', 'image']
    template_name = 'albums/photo_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album_pk = self.kwargs.get('album_pk')
        context['album'] = get_object_or_404(Album, pk=album_pk)
        context['tags'] = Tag.objects.all()
        return context

    def form_valid(self, form):
        album_pk = self.kwargs.get('album_pk')
        album = get_object_or_404(Album, pk=album_pk)
        form.instance.album = album
        
        response = super().form_valid(form)
        
        # Process and associate tags
        tags_input = self.request.POST.get('tags_input', '').strip()
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                self.object.tags.add(tag)
        
        # Log photo upload action
        AuditLog.objects.create(
            user=self.request.user,
            action="PHOTO_UPLOAD",
            details=f"Uploaded photo: '{self.object.title}' to album '{album.title}' (Album ID {album.id})",
            ip_address=get_client_ip(self.request)
        )
        messages.success(self.request, "Photo uploaded successfully!")
        return response

    def get_success_url(self):
        return reverse('album_detail', kwargs={'pk': self.kwargs.get('album_pk')})


class PhotoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Handles deleting a Photo. Checks write permissions on parent album.
    """
    model = Photo
    template_name = 'albums/photo_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        photo = self.get_object()
        album = photo.album
        # Check permissions on parent album
        if album.owner != request.user and not is_album_admin(request.user):
            AuditLog.objects.create(
                user=request.user,
                action="UNAUTHORIZED_PHOTO_DELETE_ATTEMPT",
                details=f"User '{request.user.username}' attempted to delete photo '{photo.title}' (ID {photo.id}) in album '{album.title}'",
                ip_address=get_client_ip(request)
            )
            messages.error(request, "You are not authorized to delete photos from this album.")
            return redirect('album_detail', pk=album.id)
            
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        album = self.object.album
        photo_title = self.object.title or f"Photo {self.object.id}"
        
        response = super().delete(request, *args, **kwargs)
        
        # Log photo delete action
        AuditLog.objects.create(
            user=request.user,
            action="PHOTO_DELETE",
            details=f"Deleted photo: '{photo_title}' from album '{album.title}' (Album ID {album.id})",
            ip_address=get_client_ip(request)
        )
        messages.success(request, f"Photo '{photo_title}' was successfully deleted.")
        return response

    def get_success_url(self):
        return reverse('album_detail', kwargs={'pk': self.object.album.id})


class PhotoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Handles updating a Photo's details (title, description, tags).
    """
    model = Photo
    fields = ['title', 'description']
    template_name = 'albums/photo_form.html'

    def dispatch(self, request, *args, **kwargs):
        photo = self.get_object()
        album = photo.album
        # Check permissions on parent album
        if album.owner != request.user and not is_album_admin(request.user):
            messages.error(request, "You are not authorized to edit photos in this album.")
            return redirect('album_detail', pk=album.id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['album'] = self.object.album
        context['is_edit'] = True
        # Prepopulate tag list in form
        context['tag_list'] = ", ".join([tag.name for tag in self.object.tags.all()])
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Update tags
        tags_input = self.request.POST.get('tags_input', '').strip()
        self.object.tags.clear()
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                self.object.tags.add(tag)
                
        # Log photo update action
        AuditLog.objects.create(
            user=self.request.user,
            action="PHOTO_UPDATE",
            details=f"Updated photo: '{self.object.title}' details in album '{self.object.album.title}'",
            ip_address=get_client_ip(self.request)
        )
        messages.success(self.request, "Photo details updated successfully!")
        return response

    def get_success_url(self):
        return reverse('album_detail', kwargs={'pk': self.object.album.id})


# -------------------------------------------------------------
# Admin Control Panel Views
# -------------------------------------------------------------

class AdminDashboardView(UserPassesTestMixin, TemplateView):
    """
    Premium and highly operational Admin Dashboard.
    Provides analytics, operational audits, and security metrics for Album Administrators.
    """
    template_name = 'albums/admin_dashboard.html'

    def test_func(self):
        return is_album_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User stats
        context['total_users'] = User.objects.count()
        context['active_users_today'] = User.objects.filter(last_login__date=timezone.now().date()).count()
        
        # Content stats
        context['total_albums'] = Album.objects.count()
        context['total_photos'] = Photo.objects.count()
        context['public_albums'] = Album.objects.filter(is_private=False).count()
        context['private_albums'] = Album.objects.filter(is_private=True).count()
        
        # Categorized usage data
        context['categories_stats'] = Category.objects.all()
        
        # Security Auditing Log (last 100 entries)
        context['audit_logs'] = AuditLog.objects.all().select_related('user')[:100]
        
        return context


# -------------------------------------------------------------
# Authentication & Custom Identity Views
# -------------------------------------------------------------

class CustomLoginView(LoginView):
    """
    Custom styled login view that tracks security audits.
    """
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            action="USER_LOGIN",
            details=f"User logged in successfully.",
            ip_address=get_client_ip(self.request)
        )
        messages.success(self.request, f"Welcome back, {self.request.user.username}!")
        return response


class CustomLogoutView(LogoutView):
    """
    Custom logout view that tracks security audits and cleanly logs out.
    """
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action="USER_LOGOUT",
                details=f"User logged out.",
                ip_address=get_client_ip(request)
            )
            messages.info(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    """
    Allows guest visitors to register a standard account.
    """
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Register logs
        AuditLog.objects.create(
            user=self.object,
            action="USER_REGISTER",
            details=f"New user registered: '{self.object.username}'",
            ip_address=get_client_ip(self.request)
        )
        messages.success(self.request, "Account created successfully! You can now log in.")
        return response
