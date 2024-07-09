from django.urls import path

from . import views

app_name = "tool"
urlpatterns = [
    # path('tool', views.Dataset.as_view(), name="tool"),
    path('tool/image_chat', views.ImageChat.as_view()),
]
