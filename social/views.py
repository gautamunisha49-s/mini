from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, Notification, Profile, Follow
from django.contrib.auth.models import User
from .models import Post



# ==========================================
# 🏠 MAIN FEED / HOME VIEW
# ==========================================

@login_required(login_url='login')
def home_view(request):

    posts = Post.objects.all().order_by('-id')


    notifications = Notification.objects.filter(
        receiver=request.user
    ).order_by(
        '-created_at'
    )


    context = {

        'posts': posts,

        'notifications': notifications

    }


    return render(
        request,
        'home.html',
        context
    )




# ==========================================
# 👥 AUTHENTICATION
# ==========================================


def login_view(request):

    if request.user.is_authenticated:
        return redirect('home')


    if request.method == 'POST':

        user_in = request.POST.get('username')

        pass_in = request.POST.get('password')


        user = authenticate(
            request,
            username=user_in,
            password=pass_in
        )


        if user is not None:

            login(request,user)

            return redirect('home')


        else:

            return render(
                request,
                'login.html',
                {
                    'error':'Invalid username or password'
                }
            )


    return render(request,'login.html')




def register_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        user_in = request.POST.get('username')
        email_in = request.POST.get('email')
        pass_in = request.POST.get('password')

        if User.objects.filter(username=user_in).exists():

            return render(
                request,
                'register.html',
                {
                    'error': 'Username is already taken'
                }
            )

        user = User.objects.create_user(
            username=user_in,
            email=email_in,
            password=pass_in
        )

        Profile.objects.create(
            user=user
        )

        return redirect('login')

    return render(request, 'register.html')




def logout_view(request):

    logout(request)

    return redirect('login')





# ==========================================
# 📸 POST MANAGEMENT
# ==========================================


@login_required
def create_post_view(request):

    if request.method == 'POST':

        image = request.FILES.get('image')

        caption = request.POST.get(
            'caption',
            ''
        )

        caption = caption.replace('{{', '').replace('}}', '')

        if image:

            Post.objects.create(

                user=request.user,

                image=image,

                caption=caption

            )

            messages.success(
                request,
                "Post successfully uploaded!"
            )

            return redirect('home')

        else:

            messages.error(
                request,
                "Please select an image first."
            )

    return render(
        request,
        'create_post.html'
    )


@login_required
def edit_post_view(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    # ownership check
    if post.user != request.user:

        messages.error(
            request,
            "You are not authorized."
        )

        return redirect('home')


    if request.method == 'POST':

        post.caption = request.POST.get('caption', '')

        # optional image update
        image = request.FILES.get('image')

        if image:
            post.image = image

        post.save()

        messages.success(
            request,
            "Post successfully updated!"
        )

        return redirect('home')


    return render(
        request,
        'edit_post.html',
        {
            'post': post
        }
    )




@login_required
def delete_post_view(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id
    )


    if post.user == request.user:

        post.delete()


    return redirect('home')






# ==========================================
# ❤️ LIKE SYSTEM
# ==========================================


@login_required
def like_post_view(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id
    )


    if request.user in post.likes.all():


        post.likes.remove(
            request.user
        )


    else:


        post.likes.add(
            request.user
        )


        if post.user != request.user:


            Notification.objects.create(

                sender=request.user,

                receiver=post.user,

                post=post,

                message=f"{request.user.username} liked your post"

            )



    return redirect(
        f"/#post-{post.id}"
    )






# ==========================================
# 💬 COMMENT SYSTEM
# ==========================================


@login_required
def comment_post_view(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id
    )


    if request.method == 'POST':

        comment_text = request.POST.get(
            'comment',
            ''
        ).strip()



        if comment_text:


            Comment.objects.create(

                post=post,

                user=request.user,

                text=comment_text

            )



            if post.user != request.user:


                Notification.objects.create(

                    sender=request.user,

                    receiver=post.user,

                    post=post,

                    message=f"{request.user.username} commented on your post"

                )



            messages.success(
                request,
                "Comment added successfully!"
            )



    return redirect(
        f"/#post-{post.id}"
    )







# ==========================================
# 🔔 NOTIFICATIONS VIEW
# ==========================================


@login_required
def notifications_view(request):

    notifications = Notification.objects.filter(

        receiver=request.user

    ).order_by(
        '-created_at'
    )


    return render(
        request,
        'notifications.html',
        {
            'notifications':notifications
        }
    )







# ==========================================
# ❌ DELETE COMMENT
# ==========================================


@login_required
def delete_comment_view(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id
    )


    post_id = comment.post.id



    if comment.user == request.user or comment.post.user == request.user:


        comment.delete()


        messages.success(
            request,
            "Comment deleted!"
        )


    else:


        messages.error(
            request,
            "You cannot delete this comment."
        )



    return redirect(
        f"/#post-{post_id}"
    )

#my partttttt
#  PROFILE VIEW

@login_required
def profile_view(request, user_id):

    user_obj = get_object_or_404(
        User,
        id=user_id
    )

    posts = Post.objects.filter(
        user=user_obj
    ).order_by('-id')

    profile, created = Profile.objects.get_or_create(
        user=user_obj
    )

    followers_count = Follow.objects.filter(
        following=user_obj
    ).count()

    following_count = Follow.objects.filter(
        follower=user_obj
    ).count()

    is_following = Follow.objects.filter(
        follower=request.user,
        following=user_obj
    ).exists()

    context = {
        'profile_user': user_obj,
        'profile': profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following
    }

    return render(
        request,
        'profile.html',
        context
    )



#  FOLLOW / UNFOLLOW

@login_required
def follow_user(request, user_id):

    target = get_object_or_404(
        User,
        id=user_id
    )

    if request.user == target:
        return redirect(
            'profile',
            user_id=user_id
        )

    follow_obj = Follow.objects.filter(
        follower=request.user,
        following=target
    )

    if follow_obj.exists():

        follow_obj.delete()

    else:

        Follow.objects.create(
            follower=request.user,
            following=target
        )

    return redirect(
        'profile',
        user_id=user_id
    )



#  SEARCH USERS


@login_required
def search_user(request):

    query = request.GET.get(
        'q',
        ''
    )

    users = User.objects.filter(
        username__icontains=query
    )

    return render(
        request,
        'search.html',
        {
            'users': users,
            'query': query
        }
    )



#  EDIT PROFILE

@login_required
def edit_profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        profile.bio = request.POST.get(
            'bio'
        )

        if request.FILES.get(
            'profile_picture'
        ):

            profile.profile_picture = request.FILES[
                'profile_picture'
            ]

        profile.save()

        messages.success(
            request,
            'Profile updated successfully!'
        )

        return redirect(
            'profile',
            user_id=request.user.id
        )

    return render(
        request,
        'edit_profile.html',
        {
            'profile': profile
        }
    )