import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project4.settings')
django.setup()

from network.models import User, Post, Like, Follow

def seed():
    print("Seeding demo data...")
    # Clear existing data if any
    Like.objects.all().delete()
    Follow.objects.all().delete()
    Post.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

    # Create users
    alice = User.objects.create_user(username="alice", email="alice@example.com", password="password123")
    bob = User.objects.create_user(username="bob", email="bob@example.com", password="password123")
    charlie = User.objects.create_user(username="charlie", email="charlie@example.com", password="password123")
    diana = User.objects.create_user(username="diana", email="diana@example.com", password="password123")

    print(f"Created users: {alice.username}, {bob.username}, {charlie.username}, {diana.username}")

    # Create follow relationships
    Follow.objects.create(follower=bob, following=alice)
    Follow.objects.create(follower=charlie, following=alice)
    Follow.objects.create(follower=charlie, following=bob)
    Follow.objects.create(follower=diana, following=alice)
    Follow.objects.create(follower=alice, following=bob)

    # Create posts
    posts_data = [
        (alice, "Welcome to the new Network platform! Built with modern Threads/X design principles and Django. 🚀"),
        (bob, "Just started building a cool single-page social media architecture. Loving Vanilla JS + Fetch API!"),
        (charlie, "Good morning everyone! Coffee is brewing and code is compiling. Have a fantastic day! ☕💻"),
        (diana, "Design is not just what it looks like and feels like. Design is how it works. - Steve Jobs"),
        (alice, "Tip of the day: Django ORM select_related and prefetch_related save you from N+1 query traps!"),
        (bob, "Who else is following CS50 Web Programming? It's easily one of the best courses out there."),
        (charlie, "Just published a new blog post on modern CSS Grid and Flexbox layouts."),
        (alice, "Dark mode vs Light mode: which one do you prefer for coding at night?"),
        (diana, "Accessibility is essential. Always use semantic HTML, ARIA tags, and high color contrast."),
        (bob, "Exploring Python 3.12 features. The performance improvements are impressive!"),
        (alice, "Post #11 to test our smooth Bootstrap 5 pagination control!"),
        (charlie, "Post #12 to ensure 10 posts per page works seamlessly across all views.")
    ]

    created_posts = []
    for user, content in posts_data:
        p = Post.objects.create(user=user, content=content)
        created_posts.append(p)

    # Add likes
    Like.objects.create(user=bob, post=created_posts[0])
    Like.objects.create(user=charlie, post=created_posts[0])
    Like.objects.create(user=diana, post=created_posts[0])
    Like.objects.create(user=alice, post=created_posts[1])
    Like.objects.create(user=charlie, post=created_posts[1])
    Like.objects.create(user=alice, post=created_posts[2])

    print("Successfully seeded demo users, posts, followings, and likes!")

if __name__ == "__main__":
    seed()
