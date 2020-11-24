from django.shortcuts import render, redirect
from django.views.generic import View
from .stitch import *
import os
import shutil
from django.conf import settings
# Create your views here.

directories = [
    'image/keypoints',
    'image/keypoints_image_after_compare',
    'image/matcher',
    'image/ransac',
    'image/results',
]

class Index(View):
    def get(self, request):
        return render(request, "pages/index.html")

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            base = request.POST.getlist('base[]')
            for directory in directories:
                shutil.rmtree(directory)
                os.mkdir(directory)
            s = Stitch(base, 'image')
            s.run_stitch()
        return redirect('home')