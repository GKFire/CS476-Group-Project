from django.views.generic import View
from django.shortcuts import render

class Overview(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, "page_index.html")