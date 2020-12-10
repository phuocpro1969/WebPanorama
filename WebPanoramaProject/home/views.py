from django.shortcuts import render
from django.views.generic import View
from .stitch import *
from django.http import JsonResponse
import json
# Create your views here.

class Index(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.json_content = None

    def get(self, request):
        print(self.json_content)
        return render(request, "pages/index.html")

    def post(self, request, *args, **kwargs):
        if request.method == "POST" and request.is_ajax():
            base = request.POST.getlist('base[]')
            if len(base) != 0:
                s = Stitch(base, 'image')
                s.shift()
                content = {
                    'arrKeyPoints': s.arrKeyPoints,
                    'arrKeyPointsAfterCompare': s.arrKeyPointsAfterCompare,
                    'arrMatcher': s.arrMatcher,
                    'arrRansac': s.arrRansac,
                    'arrResult': s.arrResult,
                }
                self.json_content = json.dumps(content)
        return JsonResponse({'content': self.json_content}, status=200)
