# !/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import viewsets, permissions
from devop.serializers import *
from opman.models import *
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from devop.tasks import recordAssets
from django.contrib.auth.decorators import permission_required


@api_view(['GET', 'POST'])
def idc_list(request, format=None):
    if request.method == 'GET':
        snippets = Idc_Assets.objects.all()
        serializer = IdcSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = IdcSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="添加机房：{name}".format(name=request.data.get("name")),
                               type="idc", id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def idc_detail(request, id, format=None):
    try:
        snippet = Idc_Assets.objects.get(id=id)
    except Idc_Assets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = IdcSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = IdcSerializer(snippet, data=request.data)
        old_name = snippet.name
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user), content="更新资产：{name}".format(name=snippet.name), type="idc",id=id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and request.user.has_perm('OpsManage.can_delete_assets'):
        if not request.user.has_perm('OpsManage.can_delete_service_assets'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        recordAssets.delay(user=str(request.user),
                           content="删除idc：{name}".format(name=snippet.name), type="idc",id=id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def business_list(request, format=None):
    if request.method == 'GET':
        snippets = Business_Assets.objects.all()
        serializer = BusinessSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BusinessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="添加业务分组名称：{business_name}".format(business_name=request.data.get("business_name")),
                               type="business", id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def business_detail(request, id, format=None):
    try:
        snippet = Business_Assets.objects.get(id=id)
    except Business_Assets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BusinessSerializer(snippet, data=request.data)
        old_name = snippet.business_name
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="修改业务分组为：{old_name} -> {business_name}".format(old_name=old_name,
                                                                                      business_name=request.data.get(
                                                                                         "business_name")),
                               type="business", id=id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and request.user.has_perm('OpsManage.can_delete_assets'):
        if not request.user.has_perm('OpsManage.can_delete_service_assets'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        recordAssets.delay(user=str(request.user),
                           content="删除业务类型：{business_name}".format(business_name=snippet.business_name), type="business",
                           id=id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def service_list(request, format=None):
    """
    List all order, or create a server assets order.
    """
    if request.method == 'GET':
        snippets = Service_Assets.objects.all()
        serializer = ServiceSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="添加业务类型名称：{service_name}".format(service_name=request.data.get("service_name")),
                               type="service", id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def service_detail(request, id, format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = Service_Assets.objects.get(id=id)
    except Service_Assets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ServiceSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ServiceSerializer(snippet, data=request.data)
        old_name = snippet.service_name
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="修改业务类型为：{old_name} -> {service_name}".format(old_name=old_name,
                                                                                     service_name=request.data.get(
                                                                                         "service_name")),
                               type="service", id=id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and request.user.has_perm('OpsManage.can_delete_assets'):
        if not request.user.has_perm('OpsManage.can_delete_service_assets'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        recordAssets.delay(user=str(request.user),
                           content="删除业务类型：{service_name}".format(service_name=snippet.service_name), type="service",
                           id=id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def group_list(request, format=None):
    """
    List all order, or create a server assets order.
    """
    if request.method == 'GET':
        snippets = RoleList.objects.all()
        serializer = GroupSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if not request.user.has_perm('Opsmanage.change_group'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="添加用户组：{group_name}".format(group_name=request.data.get("name")), type="group",
                               id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('Opsmanage.change_group', raise_exception=True)
def group_detail(request, id, format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = RoleList.objects.get(id=id)
    except RoleList.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GroupSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = GroupSerializer(snippet, data=request.data)
        old_name = snippet.name
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="修改用户组名称：{old_name} -> {group_name}".format(old_name=old_name,
                                                                                   group_name=request.data.get("name")),
                               type="group", id=id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.has_perm('Opsmanage.delete_group'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        recordAssets.delay(user=str(request.user), content="删除用户组：{group_name}".format(group_name=snippet.group_name),
                           type="group", id=id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_required('OpsManage.can_add_zone_assets', raise_exception=True)
def zone_list(request, format=None):
    """
    List all order, or create a server assets order.
    """

    if request.method == 'GET':
        snippets = Zone_Assets.objects.all()
        serializer = ZoneSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ZoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="添加出口线路：{zone_name}".format(zone_name=request.data.get("zone_name")),
                               type="zone", id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('OpsManage.can_change_zone_assets', raise_exception=True)
def zone_detail(request, id, format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = Zone_Assets.objects.get(id=id)
    except Zone_Assets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ZoneSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        old_name = snippet.zone_name
        serializer = ZoneSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="修改出口线路类型：{old_name} -> {zone_name}".format(old_name=old_name,
                                                                                   zone_name=request.data.get(
                                                                                       "zone_name")), type="zone",
                               id=id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.can_delete_zone_assets'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        recordAssets.delay(user=str(request.user), content="删除出口线路：{zone_name}".format(zone_name=snippet.zone_name),
                           type="zone", id=id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_required('OpsManage.can_add_line_assets', raise_exception=True)
def line_list(request, format=None):
    """
    List all order, or create a server assets order.
    """
    if request.method == 'GET':
        snippets = Line_Assets.objects.all()
        serializer = LineSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = LineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="添加出口线路：{line_name}".format(line_name=request.data.get("line_name")),
                               type="line", id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('OpsManage.can_change_line_assets', raise_exception=True)
def line_detail(request, id, format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = Line_Assets.objects.get(id=id)
    except Line_Assets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LineSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = LineSerializer(snippet, data=request.data)
        old_name = snippet.line_name
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="修改出口线路类型：{old_name} -> {line_name}".format(old_name=old_name,
                                                                                   line_name=request.data.get(
                                                                                       "line_name")), type="line",
                               id=id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.can_delete_line_assets'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        recordAssets.delay(user=str(request.user), content="删除出口线路：{line_name}".format(line_name=snippet.line_name),
                           type="line", id=id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def raid_list(request, format=None):
    """
    List all order, or create a server assets order.
    """
    if request.method == 'GET':
        snippets = Raid_Assets.objects.all()
        serializer = RaidSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = RaidSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="添加Raid类型：{raid_name}".format(raid_name=request.data.get("raid_name")),
                               type="raid", id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def raid_detail(request, id, format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = Raid_Assets.objects.get(id=id)
    except Raid_Assets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RaidSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        old_name = snippet.raid_name
        serializer = RaidSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user),
                               content="修改Raid类型：{old_name} -> {raid_name}".format(old_name=old_name,
                                                                                   raid_name=request.data.get(
                                                                                       "raid_name")), type="raid",
                               id=id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.can_delete_raid_assets'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        recordAssets.delay(user=str(request.user), content="删除Raid类型：{raid_name}".format(raid_name=snippet.raid_name),
                           type="raid", id=id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def asset_list(request, format=None):
    if request.method == 'GET':
        snippets = Assets.objects.all()
        serializer = AssetsSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = AssetsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user), content="添加资产：{name}".format(name=request.data.get("name")),
                               type="assets", id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def asset_detail(request, id, format=None):
    try:
        snippet = Assets.objects.get(id=id)
    except Assets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AssetsSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AssetsSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user), content="更新资产：{name}".format(name=snippet.name), type="assets",id=id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.delete_asset_assets'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        recordAssets.delay(user=str(request.user), content="删除资产：{name}".format(name=snippet.name), type="assets",
                           id=id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def asset_server_list(request, format=None):
    if request.method == 'GET':
        snippets = Server_Assets.objects.all()
        serializer = ServerSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if (request.data.get('data')):
            data = request.data.get('data')
        else:
            data = request.data
        print(data)
        serializer = ServerSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user), content="添加服务器资产：{ip}".format(ip=data.get("ip")), type="server",
                               id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def asset_server_detail(request, id, format=None):
    try:
        snippet = Server_Assets.objects.get(id=id)
    except Server_Assets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ServerSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        '''如果更新字段包含assets则先更新总资产表'''
        print(request.data.get('data'))
        if (request.data.get('data')):
            data = request.data.get('data')
        else:
            data = request.data
        if (data.get('assets')):
            assets_data = data.pop('assets')
            try:
                assets_snippet = Assets.objects.get(id=snippet.assets.id)
                assets = AssetsSerializer(assets_snippet, data=assets_data)
            except Assets.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            if assets.is_valid():
                assets.save()
                recordAssets.delay(user=str(request.user), content="修改服务器资产：{ip}".format(ip=snippet.ip), type="server",
                                   id=id)
        print(data)
        serializer = ServerSerializer(snippet,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.can_delete_server_assets'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        try:
            assets_snippet = Assets.objects.get(id=snippet.assets.id)
            assets_snippet.delete()
            recordAssets.delay(user=str(request.user), content="删除服务器资产：{ip}".format(ip=snippet.ip), type="server",
                               id=id)
        except Assets.DoesNotExist:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def asset_net_list(request, format=None):
    """
    List all order, or create a new net assets.
    """
    if request.method == 'GET':
        snippets = Network_Assets.objects.all()
        serializer = NetworkSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if (request.data.get('data')):
            data = request.data.get('data')
        else:
            data = request.data
        serializer = NetworkSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user), content="添加网络设备资产：{ip}".format(ip=data.get("ip")), type="net",
                               id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def asset_net_detail(request, id, format=None):
    """
    Retrieve, update or delete a net assets instance.
    """
    try:
        snippet = Network_Assets.objects.get(id=id)
    except Network_Assets.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = NetworkSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        '''如果更新字段包含assets则先更新总资产表'''
        if (request.data.get('data')):
            data = request.data.get('data')
        else:
            data = request.data
        if (data.get('assets')):
            assets_data = data.pop('assets')
            try:
                assets_snippet = Assets.objects.get(id=snippet.assets.id)
                assets = AssetsSerializer(assets_snippet, data=assets_data)
            except Assets.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            if assets.is_valid():
                assets.save()
        serializer = NetworkSerializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            recordAssets.delay(user=str(request.user), content="更新网络设备资产：{ip}".format(ip=snippet.ip), type="net", id=id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.delete_net_assets'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        try:
            assets_snippet = Assets.objects.get(id=snippet.assets.id)
            assets_snippet.delete()
            recordAssets.delay(user=str(request.user), content="删除网络设备资产：{ip}".format(ip=snippet.ip), type="net", id=id)
        except Assets.DoesNotExist:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)
