#!/usr/bin/env python3
"""
Simple test script to check blog functionality
"""

from app import create_app, db
from database.models import BlogPost, User

def test_blog_simple():
    """Simple test for blog functionality"""
    app = create_app()
    
    with app.app_context():
        print("=== Simple Blog Test ===")
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@healthyrizz.com').first()
        if admin:
            print(f"✅ Admin user found: {admin.name}")
        else:
            print("❌ Admin user not found")
            return
        
        # Check all blog posts
        all_posts = BlogPost.query.all()
        print(f"📊 Total blog posts: {len(all_posts)}")
        
        # Check published posts
        published_posts = BlogPost.query.filter_by(is_published=True).all()
        print(f"✅ Published posts: {len(published_posts)}")
        
        # Check draft posts
        draft_posts = BlogPost.query.filter_by(is_published=False).all()
        print(f"📝 Draft posts: {len(draft_posts)}")
        
        if all_posts:
            print("\n=== Blog Posts ===")
            for post in all_posts:
                status = "Published" if post.is_published else "Draft"
                print(f"📝 {post.title} ({status})")
                print(f"   - Slug: {post.slug}")
                print(f"   - Category: {post.category}")
                print(f"   - Author ID: {post.author_id}")
                print()
        
        if not all_posts:
            print("💡 No blog posts found. Create one via admin panel!")
        elif not published_posts:
            print("💡 No published posts found. Publish some posts!")
        else:
            print("✅ Blog posts exist and are published!")

        # Publish the first blog post if none are published
        if all_posts and not published_posts:
            print("🔄 Publishing the first blog post...")
            post = all_posts[0]
            post.is_published = True
            post.published_date = post.published_date or post.created_at
            db.session.commit()
            print(f"✅ Published post: {post.title}")
            # Re-run the published posts check
            published_posts = BlogPost.query.filter_by(is_published=True).all()
            print(f"✅ Published posts after update: {len(published_posts)}")

if __name__ == "__main__":
    test_blog_simple() 