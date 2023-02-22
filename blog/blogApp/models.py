from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager

# Create your models here.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,self).get_queryset().filter(status ='published')


class BlogPost(models.Model):
    STATUS_CHOICES = (
    ('draft','Draft'),
    ('published','Published')
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=130, unique_for_date='publish')
    image = models.ImageField(upload_to='featured_image/%Y/%m/%d/')
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='blog_posts')
    content = RichTextUploadingField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,choices= STATUS_CHOICES, default='draft')
    tags = TaggableManager()
    class Meta:
        ordering = ('-publish',)
    def __str__(self) -> str:
        return str(self.author) +  " Blog Title: " + self.title
    
    objects = models.Manager()
    published = PublishedManager()

    def get_absolute_url(self):
        return reverse('blogApp:postDetailView', args=[self.slug])
    
    def get_comments(self):
        return self.comments.filter(parent=None).filter(active=True)


class Comment(models.Model):
    post=models.ForeignKey(BlogPost,on_delete=models.CASCADE, related_name="comments")
    name=models.CharField(max_length=50)
    email=models.EmailField()
    parent=models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    class Meta:
        ordering = ('created',)
    
    def __str__(self):
        return self.content
    
    def get_comments(self):
        return Comment.objects.filter(parent=self).filter(active=True)