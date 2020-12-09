from django.shortcuts import render, redirect
from django.views.generic import View
from .stitch import *
import os
from django.conf import settings
# Create your views here.

class Index(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.directories = [
            'image/keypoints',
            'image/keypoints_image_after_compare',
            'image/matcher',
            'image/ransac',
            'image/results',
        ]

    def get(self, request):
        return render(request, "pages/index.html")

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            base = request.POST.getlist('base[]')
            if len(base) != 0:
                for directory in self.directories:
                    if os.path.exists(directory):
                        for root, dirs, files in os.walk(directory):
                            for file in files:
                                try:
                                    os.unlink(os.path.join(directory, file))
                                except:
                                    pass
                s = Stitch(base, 'image')
                s.run_stitch()
        return redirect('home')