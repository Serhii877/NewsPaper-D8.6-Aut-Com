from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404

from .forms import PostForm
from .models import Post, Category, User
from .filters import PostFilter


from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.forms import SignupForm

from django.core.mail import send_mail


class SocSignupForm(SignupForm):
    def save(self, request):
        user = super(SocSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user



@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='author')
    if not request.user.groups.filter(name='author').exists():
        author_group.user_set.add(user)
    return redirect('/')

@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    message = "Вы в рассылке категории"
    return render(request, 'subscribe.html', {'category': category, 'message': message})

@login_required
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.remove(user)
    message = 'Вы отписались от рассылки: '
    return render(request, 'subscribe.html', {'category': category, 'message': message})



class PostList(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-time_in_comment'
    template_name = 'news.html'
    context_object_name = 'all'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name = 'author').exists()
        return context

class PostDetail(DetailView):
    model = Post
    template_name = 'one_news.html'
    context_object_name = "news"


class PostSearch(ListView):
    model = Post
    ordering = '-time_in_comment'
    template_name = 'news_search.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['curr_date'] = self.request.GET.get('time_in_comment__date__gte')
        context['curr_title'] = self.request.GET.get('title__icontains')

        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_edit.html'



    def form_valid(self, form):
        post = form.save(commit=False)
        post.choice_title = 'NE'
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = ''


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post')
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'article_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.choice_title = 'AR'
        return super().form_valid(form)


class CategoryList(LoginRequiredMixin, ListView):
    model = Post, Category
    ordering = '-time_in_comment'
    template_name = 'news_category.html'
    context_object_name = 'all'
    paginate_by = 10

    def get_queryset(self):
        self.queryset = Category.objects.get(pk=self.kwargs['pk']).post_set.all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_not_subscriber"] = self.request.user not \
            in Category.objects.get(id=self.kwargs['pk']).subscribers.all()
        # context['xz'] = Category.objects.get(id=self.kwargs['pk']).subscribers.all()
        # #context['xz2'] = self.request.category.id
        return context
