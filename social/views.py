from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, Notification, Profile, Follow
from django.http import HttpResponseRedirect

# --- HOME VIEW ---
@login_required(login_url='login')
def home_view(request):
    posts = Post.objects.all().order_by('-id')
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    
    query = request.GET.get('q', '')
    users = []
    if query:
        users = User.objects.filter(username__icontains=query)

    context = {
        'posts': posts,
        'notifications': notifications,
        'users': users,
        'query': query,
    }
    return render(request, 'home.html', context)


# --- AUTHENTICATION ---
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

        user = User.objects.create_user(username=user_in, email=email_in, password=pass_in)
        Profile.objects.create(user=user)
        return redirect('login')

    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# --- POST MANAGEMENT ---
@login_required
def create_post_view(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '').replace('{{', '').replace('}}', '')

        if image:
            Post.objects.create(user=request.user, image=image, caption=caption)
            messages.success(request, "Post successfully uploaded!")
            return redirect('home')
        else:
            messages.error(request, "Please select an image first.")

    return render(request, 'create_post.html')


@login_required
def edit_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        messages.error(request, "You are not authorized.")
        return redirect('home')

    if request.method == 'POST':
        post.caption = request.POST.get('caption', '')
        image = request.FILES.get('image')
        if image:
            post.image = image
        post.save()
        messages.success(request, "Post successfully updated!")
        return redirect('home')

    return render(request, 'edit_post.html', {'post': post})


@login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
    return redirect('home')


# --- LIKE SYSTEM ---
@login_required
def like_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        if post.user != request.user:
            Notification.objects.create(
                sender=request.user,
                receiver=post.user,
                post=post,
                message=f"{request.user.username} liked your post"
            )
    return redirect(f"/#post-{post.id}")


# --- COMMENT SYSTEM ---
@login_required
def comment_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()

        if comment_text:
            Comment.objects.create(post=post, user=request.user, text=comment_text)
            if post.user != request.user:
                Notification.objects.create(
                    sender=request.user,
                    receiver=post.user,
                    post=post,
                    message=f"{request.user.username} commented on your post"
                )
            messages.success(request, "Comment added successfully!")

    return redirect(f"/#post-{post.id}")


@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id

    if comment.user == request.user or comment.post.user == request.user:
        comment.delete()
        messages.success(request, "Comment deleted!")
    else:
        messages.error(request, "You cannot delete this comment.")

    return redirect(f"/#post-{post_id}")


# --- NOTIFICATIONS ---
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    following_users = Follow.objects.filter(
        follower=request.user
    ).values_list('following_id', flat=True)

    return render(request, 'notifications.html', {
        'notifications': notifications,
        'following_users': following_users,
    })


# --- PROFILE VIEW ---
@login_required
def profile_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(user=user_obj).order_by('-id')
    profile, created = Profile.objects.get_or_create(user=user_obj)

    followers_count = Follow.objects.filter(following=user_obj).count()
    following_count = Follow.objects.filter(follower=user_obj).count()
    is_following = Follow.objects.filter(follower=request.user, following=user_obj).exists()

    context = {
        'profile_user': user_obj,
        'profile': profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following
    }
    return render(request, 'profile.html', context)


# --- FOLLOW / UNFOLLOW ---
@login_required
def follow_user(request, user_id):
    target = get_object_or_404(User, id=user_id)

    if request.user == target:
        return redirect('profile', user_id=user_id)

    follow = Follow.objects.filter(follower=request.user, following=target)

    if follow.exists():
        follow.delete()
        # maile pathaeko "started following you" notification pani hataune
        Notification.objects.filter(
            sender=request.user,
            receiver=target,
            message__icontains="following you"
        ).delete()
    else:
        Follow.objects.create(
            follower=request.user, 
            following=target
            )
        Notification.objects.create(
            sender=request.user,
            receiver=target,
            message="Started following you."
        )

    return redirect('profile', user_id=user_id)


@login_required
def follow_back(request, user_id):
    target = get_object_or_404(User, id=user_id)

    # Don't allow following yourself
    if request.user == target:
        return redirect('notifications')

    follow = Follow.objects.filter(follower=request.user, following=target)
    print(follow)
    if follow.exists():
        # already following -> yo click le unfollow garcha (toggle)
        follow.delete()
        Notification.objects.filter(
            sender=request.user,
            receiver=target,
            message__icontains="following you"
        ).delete()
    else:
        Follow.objects.create(
            follower=request.user,
            following=target
        )
        Notification.objects.create(
            sender=request.user,
            receiver=target,
            message="Started following you."
        )

    return redirect('notifications')


# --- FOLLOWERS / FOLLOWING LIST ---
@login_required
def followers_list_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    follows = Follow.objects.filter(following=profile_user).select_related('follower')
    people = [f.follower for f in follows]

    my_following_ids = set(
        Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    )

    return render(request, 'follow_list.html', {
        'profile_user': profile_user,
        'people': people,
        'list_title': 'Followers',
        'my_following_ids': my_following_ids,
    })


@login_required
def following_list_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    follows = Follow.objects.filter(follower=profile_user).select_related('following')
    people = [f.following for f in follows]

    my_following_ids = set(
        Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    )

    return render(request, 'follow_list.html', {
        'profile_user': profile_user,
        'people': people,
        'list_title': 'Following',
        'my_following_ids': my_following_ids,
    })


# --- SEARCH USERS ---
@login_required

def search_user(request):
    query = request.GET.get('q', '').strip()

    if query:
        users = User.objects.filter(
            username__istartswith=query
        ).order_by('username')
    else:
        users = []

    return render(request, 'search.html', {
        'users': users,
        'query': query,
    })


# --- EDIT PROFILE ---
@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.bio = request.POST.get('bio')
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile', user_id=request.user.id)

    return render(request, 'edit_profile.html', {'profile': profile})


# --- FIXED TOGGLE DARK MODE ---
def toggle_dark_mode(request):
    current_theme = request.session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    request.session['theme'] = new_theme
    
    # HTTP_REFERER (user कुन page बाट आएको हो त्यहीँ फिर्ता पठाउने)
    response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return response


# --- DELETE NOTIFICATION ---
@login_required
def delete_notification_view(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if notification.receiver == request.user:
        notification.delete()
        messages.success(request, "Notification deleted.")
    else:
        messages.error(request, "You cannot delete this notification.")

    return redirect('notifications') 