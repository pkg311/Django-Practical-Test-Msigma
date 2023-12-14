from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .form import UserRegistrationForm, PostCreationForm, UserLoginForm
from .models import CustomUser, Post
from django.http import JsonResponse
import re


class UserRegistrationView(View):
    form_class = UserRegistrationForm
    template_name = 'registration/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
        return render(request, self.template_name, {'form': form})

class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'registration/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                request.session['userlogin']=user.email
                request.session['name']=user.first_name
                login(request, user)
                return redirect('post_list')  # Redirect to post list page after successful login
        return render(request, self.template_name, {'form': form, 'error': 'Invalid credentials'})

class UserLogoutView(View):
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request):
        if request.session['userlogin']:
            del request.session['userlogin']
            del request.session['name']
        logout(request)
        return redirect('post_list')  # Redirect to post list or any desired page after logout

# Other views for Post-related operations (placeholders)
class PostCreateView(View):
    form_class = PostCreationForm
    template_name = 'create_post.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            # Extract usernames from content using regex (assuming @username pattern)
            tagged_users = re.findall(r'@(\w+)', content)

            # Process tagged users and replace usernames in content with hyperlinks
            for username in tagged_users:
                try:
                    user = CustomUser.objects.get(username=username)
                    full_name = f"{user.first_name} {user.last_name}"
                    content = content.replace(f"@{username}", full_name)
                except CustomUser.DoesNotExist:
                    pass  # Handle case where user does not exist

            # Save the post (replace it with your saving logic)
            post = Post(title=title, content=content, author=request.user)
            post.save()

            return redirect('post_list')  # Redirect to post list page after post creation

        return render(request, self.template_name, {'form': form})

class PostListView(View):
    template_name = 'post_list.html' #template name html page 

    def get(self, request):
        posts = Post.objects.all()
        return render(request, self.template_name, {'posts': posts})

class PostDetailView(View):
    template_name = 'post_detail.html' #template name html page 

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        return render(request, self.template_name, {'post': post})

class PostUpdateView(View):
    template_name = 'update_post.html'  # Template name for the update post page
    form_class = PostCreationForm  # Replace with your form class for updating posts

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = self.form_class(instance=post)
        return render(request, self.template_name, {'form': form, 'post': post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)  # Get the updated post data from the form
            content = updated_post.content

            # Extract usernames from content using regex (assuming @username pattern)
            tagged_users = re.findall(r'@(\w+)', content)

            # Process tagged users and replace usernames in content with hyperlinks
            for username in tagged_users:
                try:
                    user = CustomUser.objects.get(username=username)
                    full_name = f"{user.first_name} {user.last_name}"
                    content = content.replace(f"@{username}", full_name)
                except CustomUser.DoesNotExist:
                    pass  # Handle case where user does not exist

            # Update the post title and content
            updated_post.title = form.cleaned_data['title']
            updated_post.content = content
            updated_post.save()

            return redirect('post_detail', pk=pk)  # Redirect to post detail after update

        return render(request, self.template_name, {'form': form, 'post': post})
class PostDeleteView(View):
    template_name = 'delete_post.html' #template name html page 

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        return render(request, self.template_name, {'post': post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return redirect('post_list')  # Redirect to post list after deletion

def search_users(request):
    if request.method == 'GET' and request.is_ajax():
        usernames = request.GET.getlist('usernames[]')
        matching_users = CustomUser.objects.filter(username__in=usernames).values_list('username', flat=True)
        return JsonResponse({'users': list(matching_users)})
    return JsonResponse({'error': 'Invalid request'})