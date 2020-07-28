from django.shortcuts import render


def index(request):
    return render(request, 'reports.html', {
        'title': '多端报警系统'
    })

