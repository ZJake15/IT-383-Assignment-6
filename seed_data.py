import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group
from albums.models import Category, Tag, Album, Photo, AuditLog

def seed():
    print("Starting database seeding...")
    
    # 1. Create Album Administrators group
    admin_group, created = Group.objects.get_or_create(name='Album Administrators')
    if created:
        print("Created group: 'Album Administrators'")
    
    # 2. Create Album Administrator User
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@photoalbum.com',
            password='adminpassword123'
        )
        # Add to group
        admin_user.groups.add(admin_group)
        print("Created superuser 'admin' with password 'adminpassword123'")
    else:
        admin_user = User.objects.get(username='admin')
        admin_user.groups.add(admin_group)
        print("Superuser 'admin' already exists, added to group")

    # 3. Create Standard Users
    if not User.objects.filter(username='user1').exists():
        user1 = User.objects.create_user(
            username='user1',
            email='user1@photoalbum.com',
            password='userpassword123'
        )
        print("Created user 'user1' with password 'userpassword123'")
    else:
        user1 = User.objects.get(username='user1')

    if not User.objects.filter(username='user2').exists():
        user2 = User.objects.create_user(
            username='user2',
            email='user2@photoalbum.com',
            password='userpassword123'
        )
        print("Created user 'user2' with password 'userpassword123'")
    else:
        user2 = User.objects.get(username='user2')

    # 4. Create Categories
    categories = [
        ('Nature', 'Scenic landscapes, wildlife, and natural wonders'),
        ('Travel', 'Adventures around the globe, cities, and cultural trips'),
        ('Family', 'Cherished family moments, events, and portraits'),
        ('Portraits', 'Studio, outdoor, and creative close-ups'),
        ('Street', 'Candid moments captured in urban environments'),
        ('Architecture', 'Stunning structural designs and historical buildings')
    ]
    
    for name, desc in categories:
        cat, created = Category.objects.get_or_create(name=name, defaults={'description': desc})
        if created:
            print(f"Created category: {name}")

    # 5. Create Tags
    tags = ['Adventure', 'Sunset', 'Scenic', 'Memories', 'Retro', 'Minimalist', 'Urban', 'Cozy']
    for t_name in tags:
        tag, created = Tag.objects.get_or_create(name=t_name)
        if created:
            print(f"Created tag: #{t_name}")

    # 6. Create Initial Public Album for user1
    nature_cat = Category.objects.get(name='Nature')
    if not Album.objects.filter(title="Summer Wanderlust", owner=user1).exists():
        album1 = Album.objects.create(
            title="Summer Wanderlust",
            description="A visual diary of my travel and nature explorations during the beautiful summer season. Captured in high resolution.",
            owner=user1,
            category=nature_cat,
            is_private=False
        )
        print(f"Created public album: '{album1.title}' for user1")
        
        # Log action
        AuditLog.objects.create(
            user=user1,
            action="ALBUM_CREATE",
            details=f"Created public album: '{album1.title}'",
            ip_address="127.0.0.1"
        )

    # 7. Create Private Album for user2
    family_cat = Category.objects.get(name='Family')
    if not Album.objects.filter(title="Confidential Family Archive", owner=user2).exists():
        album2 = Album.objects.create(
            title="Confidential Family Archive",
            description="Highly confidential family memories. Only visible to me and system administrators.",
            owner=user2,
            category=family_cat,
            is_private=True
        )
        print(f"Created private album: '{album2.title}' for user2")
        
        # Log action
        AuditLog.objects.create(
            user=user2,
            action="ALBUM_CREATE",
            details=f"Created private album: '{album2.title}' (Private)",
            ip_address="127.0.0.1"
        )

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()
