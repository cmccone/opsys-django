#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import viewsets, permissions
from devop.serializers import *
from opman.models import *
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from devop.tasks import recordProject
from django.contrib.auth.decorators import permission_required
from rest_framework import generics
from django.db.models import Q


@api_view(['GET', 'POST'])
@permission_required('OpsManage.can_add_project_config', raise_exception=True)
def deploy_list(request, format=None):
    """
    List all order, or create a server assets order.
    """
    if request.method == 'GET':
        snippets = Project_Config.objects.all()
        serializer = ProjectConfigSerializer(snippets, many=True)
        return Response(serializer.data)

#     elif request.method == 'POST':
#         serializer = ProjectConfigSerializer(data=request.data)
#
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('OpsManage.can_delete_project_config', raise_exception=True)
def deploy_detail(request, id, format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = Project_Config.objects.get(id=id)
    except Project_Config.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectConfigSerializer(snippet)
        return Response(serializer.data)

#     elif request.method == 'PUT':
#         serializer = ProjectConfigSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.delete_project_config'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        recordProject.delay(project_user=str(request.user), project_id=id, project_name=snippet.project_name, project_content="删除项目")
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderList(generics.ListAPIView):
    serializer_class = DeployOrderSerializer

    def get_queryset(self):
        user = self.request.user
        username = self.kwargs['username']
        if str(user) == str(username):
            return Project_Order.objects.filter(Q(order_user=user) | Q(order_audit=user), order_status__in=[0, 2]).order_by("id")
        else:
            return []
