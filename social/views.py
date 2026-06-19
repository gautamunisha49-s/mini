from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment  # 🎯 यहाँ 'Comment' पनि इम्पोर्ट गरियो

# ==========================================
# 🏠 १. MAIN FEED / HOME VIEW
# ==========================================
@login_required(login_url='login')
def home_view(request):
    # नयाँ पोस्ट सधैँ माथि देखिने गरी डेटाबेसबाट तान्ने
    posts = Post.objects.all().order_by('-id') 
    
    context = {
        'posts': posts, 
        'recent_stories': []
    }
    return render(request, 'home.html', context)


# ==========================================
# 👥 २. AUTHENTICATION VIEWS
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        user_in = request.POST.get('username')
        pass_in = request.POST.get('password')
        
        user = authenticate(request, username=user_in, password=pass_in)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
            
    return render(request, 'login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        user_in = request.POST.get('username')
        email_in = request.POST.get('email')
        pass_in = request.POST.get('password')
        
        if User.objects.filter(username=user_in).exists():
            return render(request, 'register.html', {'error': 'Username is already taken'})
            
        User.objects.create_user(username=user_in, email=email_in, password=pass_in)
        return redirect('login')
        
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ==========================================
# 📸 ३. POST MANAGEMENT
# ==========================================

# Create Post
@login_required
def create_post_view(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '')
        
        if image:
            Post.objects.create(user=request.user, image=image, caption=caption)
            messages.success(request, "Post successfully uploaded!")
            return redirect('home')
        else:
            messages.error(request, "Please select an image first.")
            
    return render(request, 'create_post.html', {'title': 'Create Post'})


# Edit Post
@login_required
def edit_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if post.user != request.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('home')
        
    if request.method == 'POST':
        caption = request.POST.get('caption', '')
        if request.FILES.get('image'):
            post.image = request.FILES.get('image')
        post.caption = caption
        post.save()
        messages.success(request, "Post updated successfully!")
        return redirect('home')
        
    return render(request, 'create_post.html', {'post': post, 'title': 'Edit Post'})


# Delete Post
@login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if post.user != request.user:
        messages.error(request, "You cannot delete this post.")
        return redirect('home')
        
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully.")
    return redirect('home')


# ==========================================
# ❤️ ४. LIKE & COMMENT SYSTEM (सच्याइएको भाग)
# ==========================================

# 🔴 लाइक गर्ने फङ्कसन (इन्स्टाग्राम जस्तै एउटै ठाउँमा स्क्रिन रोक्ने गरी)
@login_required
def like_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    # 🎯 यहाँ एङ्कर ट्याग हालेर पठाइयो, अब लाइक गर्दा पेज टपमा कुद्दैन!
    return redirect(f"/#post-{post.id}")


# 💬 कमेन्ट गर्ने फङ्कसन (डेटाबेसमा कमेन्ट सेभ हुने गरी)
@login_required
def comment_post_view(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            # 🎯 अन-कमेन्ट गरियो! अब कमेन्ट सिधै डेटाबेसमा सेभ हुन्छ।
            Comment.objects.create(post=post, user=request.user, text=comment_text)
            messages.success(request, "Comment added successfully!")
    return redirect(f"/#post-{post.id}")

@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    
    # कमेन्ट गर्ने मान्छे वा पोस्टको मालिकले मात्र डिलिट गर्न पाओस्
    if comment.user == request.user or comment.post.user == request.user:
        comment.delete()
        messages.success(request, "Comment deleted!")
    else:
        messages.error(request, "You cannot delete this comment.")
        
    return redirect(f"/#post-{post_id}")