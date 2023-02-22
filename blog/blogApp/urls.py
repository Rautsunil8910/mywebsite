from django.urls import path
from .import views
app_name =' blogApp'
urlpatterns = [ 
    path('',views.postList, name='postList'),
    path('<slug:post>/',views.PostDetailView, name='postDetailView'),
    path('comment/reply/', views.reply_page, name="reply"),
    path('tag/<slug:tag_slug>/',views.postList, name='post_tag'),
]