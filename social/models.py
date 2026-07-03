from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    # Django ko User model sanga link gariyo
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts_images/')
    caption = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # like maa heart ko chitra
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
         ordering = ['-created_at']  

    def __str__(self):
        return f"{self.user.username}'s post - {self.created_at.strftime('%Y-%m-%d')}"


#  comment save garna naya model banayeko
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # purana commenet maathi , naya tala dekhinchha

    def __str__(self):
        return f"{self.user.username}: {self.text[:20]}"
    
    #interactions

class Notification(models.Model):

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_notifications'
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    message = models.CharField(
        max_length=200
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return self.message
   
   #mypartttt
   

class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    bio = models.TextField(
        blank=True
    )

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='default.png'
    )

    def __str__(self):
        return self.user.username


class Follow(models.Model):

    follower = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    following = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            'follower',
            'following'
        )

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"