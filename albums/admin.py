from django.contrib import admin
from .models import Category, Tag, Album, Photo, AuditLog

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'is_private', 'created_at')
    list_filter = ('is_private', 'category', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    date_hierarchy = 'created_at'

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'album', 'title', 'uploaded_at')
    list_filter = ('uploaded_at', 'album__category')
    search_fields = ('title', 'description', 'album__title')
    filter_horizontal = ('tags',)
    date_hierarchy = 'uploaded_at'

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('action', 'details', 'user__username', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'action', 'details', 'timestamp', 'ip_address')
