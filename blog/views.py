# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Comment

from .forms import PostForm, CommentForm, ContactForm

from django.core.mail import EmailMessage

from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage
# Create your views here.

def post_list(request, page=1):
	posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
	paginator = Paginator (posts, 9)
        random = Post.objects.order_by('?')[:2]
	try:
		posts = paginator.page(page)
	except EmptyPage:
		posts = paginator.page(paginator.num_pages)
	return render(request, 'blog/post_list.html', {'posts': posts,'random': random})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    random = Post.objects.order_by('?')[:2]
    return render(request, 'blog/post_detail.html', {'post': post,'random': random})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
	random = Post.objects.order_by('?')[:2]
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form,'random': random})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    random = Post.objects.order_by('?')[:2]
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form,'random': random})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    random = Post.objects.order_by('?')[:2]
    return render(request, 'blog/post_draft_list.html', {'posts': posts,'random': random})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    random = Post.objects.order_by('?')[:2]
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form,'random': random})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)

def contact(request):
    form_class = ContactForm
    random = Post.objects.order_by('?')[:2]
    # new logic!
    if request.method == 'POST':
        form = form_class(data=request.POST)

        if form.is_valid():
            contact_name = request.POST.get('contact_name', '')
            contact_email = request.POST.get('contact_email', '')
            form_content = request.POST.get('content', '')

            # Email the profile with the
            # contact information
            template = get_template('blog/contact_template.txt')
            context = {
                'contact_name': contact_name,
                'contact_email': contact_email,
                'form_content': form_content,
            }
            content = template.render(context)

            email = EmailMessage(
                "New contact form submission", content, "Your website" +'',
                ['youremail@gmail.com'],
                headers = {'Reply-To': contact_email }
            )
            email.send()
            return redirect('contact')

    return render(request, 'blog/contact.html', {'form': form_class,'random': random})


def infos(request):
    random = Post.objects.order_by('?')[:2]
    return render(request, 'blog/infos.html',{'random': random})

