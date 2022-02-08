from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

QTY_OF_POSTS_ON_PAGE = 10


class Index(ListView):
    template_name = 'posts/index.html'
    model = Post
    context_object_name = 'posts'
    extra_context = {'title': 'Это главная страница проекта Yatube'}
    paginate_by = QTY_OF_POSTS_ON_PAGE


class GroupPosts(ListView):
    template_name = 'posts/group_list.html'
    context_object_name = 'posts'
    paginate_by = QTY_OF_POSTS_ON_PAGE

    def get_queryset(self, **kwargs):
        self.group = get_object_or_404(Group, slug=self.kwargs['group_list'])
        return self.group.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context


class Profile(ListView):
    template_name = 'posts/profile.html'
    context_object_name = 'posts'
    paginate_by = QTY_OF_POSTS_ON_PAGE

    def get_queryset(self, **kwargs):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return self.author.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        user = self.request.user
        context['following'] = (self.request.user.is_authenticated
                                and user.follower.filter
                                (author=self.author.id).exists())
        return context


class PostDetail(DetailView):
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_count'] = Post.objects.filter(
            author_id=self.object.author).count()
        context['comments'] = self.object.comments.all()
        context['form'] = CommentForm(self.request.POST or None)
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('posts:profile',
                            kwargs={'username': self.request.user.username})


class PostEdit(LoginRequiredMixin, UpdateView):
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if (self.request.user.is_authenticated
                and post.author != self.request.user):
            return redirect('posts:post_detail', pk=post.id)
        return super(PostEdit, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.object.id
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('posts:post_detail',
                            kwargs={'pk': self.object.id})


class AddComment(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('posts:post_detail',
                            kwargs={'pk': self.kwargs['pk']})


class FollowIndex(LoginRequiredMixin, ListView):
    template_name = 'posts/follow.html'
    context_object_name = 'posts'
    paginate_by = QTY_OF_POSTS_ON_PAGE

    def get_queryset(self, **kwargs):
        user = self.request.user
        authors = user.follower.all().values('author')
        return Post.objects.filter(author__in=authors)


class ProfileFollow(LoginRequiredMixin, View):
    def get(self, request, username):
        user = self.request.user
        author = get_object_or_404(User, username=username)
        if (user != author and not
                user.follower.filter(author=author.id).exists()):
            follow = Follow(user=user, author=author)
            follow.save()
        return redirect('posts:profile', username=username)


class ProfileUnfollow(LoginRequiredMixin, View):
    def get(self, request, username):
        user = self.request.user
        author = get_object_or_404(User, username=username)
        follow = user.follower.get(author=author.id)
        follow.delete()
        return redirect('posts:profile', username=username)
