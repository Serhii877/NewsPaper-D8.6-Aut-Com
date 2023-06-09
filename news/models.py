from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
import django


class Author(models.Model):
    user_author = models.OneToOneField(User, on_delete=models.CASCADE)
    user_rating = models.IntegerField(default=0)


    def __str__(self):
        return f'{self.user_author.first_name}'

    def update_rating(self):
        rating_posts_author = \
            Post.objects.filter(author=self).aggregate(Sum('rating_post')).get('rating_post__sum') * 3
        rating_comments_author = \
            Comment.objects.filter(user_comment=self.user_author).aggregate(Sum('rating_comment')).get(
                'rating_comment__sum')
        rating_comments_posts = \
            Comment.objects.filter(post_comment__author=self).aggregate(Sum('rating_comment')).get(
                'rating_comment__sum')
        self.user_rating = rating_posts_author + rating_comments_author + rating_comments_posts
        print(self.user_rating)
        self.save()


class Category(models.Model):
    objects = None

    economy = 'EC'
    politician = 'PL'
    worldnews = 'WN'
    hostnews = 'HN'
    sport = 'SP'

    POSITION = [
        (economy, 'Экономика'),
        (politician, 'Политика'),
        (worldnews, 'Мировые новости'),
        (hostnews, 'Местные новости'),
        (sport, 'Спортивные новости')
    ]

    category = models.CharField(max_length=2, choices=POSITION, default='HN', unique=True)
    subscribers = models.ManyToManyField(User, blank=True, related_name='categories')

    def __str__(self):
        return self.category

    def __str__(self):
        return self.get_category_display()




class Post(models.Model):
    objects = None
    article = 'AR'
    news = 'NE'
    POST = [
        (news, 'Новость'),
        (article, 'Статья')
    ]
    title = models.TextField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    time_in_comment = models.DateTimeField(default=django.utils.timezone.now)
    choice_title = models.CharField(max_length=2, choices=POST)
    post_text = models.TextField(max_length=500)
    categories = models.ManyToManyField('Category', through='PostCategory')

    rating_post = models.IntegerField(default=0)

    def preview(self):
        return self.post_text[:124] + '...'

    def like(self):
        self.rating_post += 1
        self.save()

    def dislike(self):
        self.rating_post -= 1
        self.save()

    def __str__(self):
        return self.get_choice_title_display()



    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class PostCategory(models.Model):
    Post = models.ForeignKey(Post, on_delete=models.CASCADE)
    Category = models.ForeignKey(Category, on_delete=models.CASCADE)


class PostSubscribers(models.Model):
    Category = models.ForeignKey(Category, on_delete=models.CASCADE)
    User = models.ForeignKey(User, on_delete=models.CASCADE)



class Comment(models.Model):
    objects = None
    post_comment = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_comment = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=500, null=True)
    time_in_comment = models.DateTimeField(auto_now_add=True)
    rating_comment = models.IntegerField(default=0)

    def like(self):
        self.rating_comment += 1
        self.save()

    def dislike(self):
        self.rating_comment -= 1
        self.save()
