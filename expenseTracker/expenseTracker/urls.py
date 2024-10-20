"""
URL configuration for expenseTracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# Existing about_me_data dictionary
about_me_data = {
    "name": "Meet Kothari",
    "education": "Pursuing post-graduation at the Dhirubhai Ambani Institute of Information and Communication Technology",
    "about": "With a strong background in data engineering, I have experience with technologies like Python, Apache Airflow, SQL, AWS, Docker, and BigQuery.",
    "resume_link": "https://drive.google.com/file/d/1JdXJR5ZBGbcPkslxHYLH3ZPiYYQzJnIt/view?usp=sharing",
    "github_link": "https://github.com/MeetK208/",
    "linkedin": "https://www.linkedin.com/in/meetkothari208/",
    "email": "meetkothari208@gmail.com"
}

def about_me_view(request):
    return JsonResponse(about_me_data)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('user.urls')),
    path('expenses/', include('expense.urls')),
    path('balance/', include('balancesheet.urls')),
    path('about/', about_me_view, name='about_me'),  # Add this line
]
