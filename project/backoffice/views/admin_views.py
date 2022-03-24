from django.contrib.auth.models import Group, User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from backoffice.permissions import OwnerPermission, AdminPermission, ManagerPermission
from backoffice.serializers import AdminLoginSerializer, AdminSerializer
from home.models import Admin


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission])
def admin_list(request):
    admins = Admin.objects.all()
    paginator = PageNumberPagination()
    paginator.page_size = 12
    page = paginator.paginate_queryset(admins, request)
    serializer = AdminSerializer(
        page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission])
def add_new_admin(request):
    data=request.data
    user = User.objects.create_user(first_name=data['first_name'], username=data['username'], password=data['password'])
    user.groups.add(Group.objects.get(name=data['role']))
    user.save()
    
    admin = Admin.objects.create(admin=user, promoted_by=request.user, image=data.get('image'))
    admin.save()
    
    return Response({'status': 'ok'})


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission])
def edit_admin(request, id):
    data = request.data
    admin = Admin.objects.get(id=id) 
    user = User.objects.get(id=admin.admin.id)
    user.first_name = data.get('first_name')
    user.username = data.get('username')
    user.groups.add(Group.objects.get(name=data['role']))
    user.set_password(data['password'])
    user.save()

    admin = Admin.objects.update(admin=user, promoted_by=request.user)
    admin.save()

    return Response({'status': 'ok'})


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission])
def delete_admin(request, id):
    admin = Admin.objects.get(id=id)
    admin.admin.delete()
    admin.delete()
    return Response({'status': 'ok'})