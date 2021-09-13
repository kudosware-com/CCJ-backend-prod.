from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .pdflist import recommend_pdf
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from ccj import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.core.cache import caches,cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# Serve Single Page Application
index = never_cache(TemplateView.as_view(template_name='index.html'))

@api_view(['GET'])
def search_pdf_view(request, expression):
    """
        retrieve:
            Returns relevant files with scores

    """
    if request.method == 'GET':
        page = request.GET.get('page')
        if(request.GET.get('page') == None):
            temp_list,keys = recommend_pdf(expression)
            request.session["myCached"] = temp_list
            page = 1
        else:
            temp_list = request.session["myCached"]
        paginator = Paginator(temp_list, 4)
        page = request.GET.get('page')
        try:
            pdf_list = paginator.page(page)
        except PageNotAnInteger:
            pdf_list = paginator.page(1)
        except EmptyPage:
            page = paginator.num_pages
            pdf_list = paginator.page(paginator.num_pages)

        if(request.GET.get('page') == None):
            return Response(data=
                        {
                        'page': page,
                        'prev':pdf_list.has_previous(),
                        'next':pdf_list.has_next(),
                        'pdf_list': pdf_list,
                        'keys':keys
                        },status=status.HTTP_200_OK)
        else:
            return Response(data=
                        {
                        'page': page,
                        'prev':pdf_list.has_previous(),
                        'next':pdf_list.has_next(),
                        'pdf_list': pdf_list,
                        },status=status.HTTP_200_OK)

