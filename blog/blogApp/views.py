from django.shortcuts import render, get_object_or_404
from . models import BlogPost, Comment
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import CommentForm
from django.shortcuts import redirect
from taggit.models import Tag
from django.db.models import Count
from django.db.models import Q

# Create your views here.
def postList(request, tag_slug = None):
    post = BlogPost.published.all()
    paginator = Paginator(post, 10) # 10 posts in each page
    page = request.GET.get('page')
    tag = None
    query = request.GET.get("q")
    if query:
        post = BlogPost.published.filter(Q(title__icontains=query) | Q(tags__name__icontains=query)).distinct()
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post = post.filter(tags__in=[tag])
    try:
        post = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        post = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        post = paginator.page(paginator.num_pages)
 
    return render(request,'blogApp/post_list.html',{'posts':post, page:'pages','tag':tag})

def PostDetailView(request, post):
     post=get_object_or_404(BlogPost,slug=post,status='published')
     comments = post.comments.filter(active=True)
     comment_form = CommentForm()
     new_comment = None
     if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
            # redirect to same page and focus on that comment
            return redirect(post.get_absolute_url()+'#'+str(new_comment.id))
        else:
            comment_form = CommentForm()
        # List of similar posts
     post_tags_ids = post.tags.values_list('id', flat=True)
     similar_posts = BlogPost.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
     similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:6]

    
     return render(request, 'blogApp/post_detail.html',{'post':post,'comments': comments,'comment_form':comment_form, 'similar_posts':similar_posts})

# handling reply, reply view
def reply_page(request):
    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():
            post_id = request.POST.get('post_id')  # from hidden input
            parent_id = request.POST.get('parent')  # from hidden input
            post_url = request.POST.get('post_url')  # from hidden input

            reply = form.save(commit=False)
    
            reply.post = BlogPost(id=post_id)
            reply.parent = Comment(id=parent_id)
            reply.save()

            return redirect(post_url+'#'+str(reply.id))

    return redirect("/")
