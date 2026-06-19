from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    # Django ko User model sanga link gariyo
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts_images/')
    caption = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 🔴 यहाँ थपियो: लाइकका लागि Many-to-Many field (इन्स्टाग्राम जस्तै रातो मुटु बनाउन)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']  # Naya post sadhai mathi dekhinchha

    def __str__(self):
        return f"{self.user.username}'s post - {self.created_at.strftime('%Y-%m-%d')}"


# 💬 यहाँ थपियो: कमेन्ट सेभ गर्नका लागि नयाँ मोडल
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # पुराना कमेन्ट माथि, नयाँ तल आउँछन्

    def __str__(self):
        return f"{self.user.username}: {self.text[:20]}"