
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import TaskForm
from .models import Task


def home(request):
    return render(request, 'tasks/home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'tasks/signup.html', {
            'form': UserCreationForm()
        })

    form = UserCreationForm(request.POST)

    if form.is_valid():
        try:
            user = form.save()
            login(request, user)
            return redirect('tasks')
        except IntegrityError:
            form.add_error('username', 'Este usuario ya existe.')

    return render(request, 'tasks/signup.html', {'form': form})


def signin(request):
    if request.method == 'GET':
        return render(request, 'tasks/signin.html', {
            'form': AuthenticationForm()
        })

    form = AuthenticationForm(request, data=request.POST)

    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('tasks')

    return render(request, 'tasks/signin.html', {'form': form})


@login_required
@require_POST
def signout(request):
    logout(request)
    return redirect('home')


@login_required
def tasks(request):
    tareas = Task.objects.filter(
        user=request.user,
        completed=False
    ).order_by('-created')

    return render(request, 'tasks/tasks.html', {
        'tasks': tareas
    })


@login_required
def tasks_completed(request):
    tareas = Task.objects.filter(
        user=request.user,
        completed=True
    ).order_by('-datecompleted')

    return render(request, 'tasks/tasks.html', {
        'tasks': tareas,
        'completed': True
    })


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'tasks/create_task.html', {
            'form': TaskForm()
        })

    form = TaskForm(request.POST)

    if form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.save()
        return redirect('tasks')

    return render(request, 'tasks/create_task.html', {
        'form': form
    })


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(
        Task, pk=task_id, user=request.user
    )

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            return redirect('tasks')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'form': form
    })


@login_required
@require_POST
def complete_task(request, task_id):
    task = get_object_or_404(
        Task, pk=task_id, user=request.user
    )
    task.completed = True
    task.datecompleted = timezone.now()
    task.save()

    return redirect('tasks')


@login_required
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(
        Task, pk=task_id, user=request.user
    )
    task.delete()

    return redirect('tasks')
