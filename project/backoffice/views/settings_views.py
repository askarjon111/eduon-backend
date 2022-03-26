from django.http import JsonResponse
from backoffice.serializers import ReferalValueSerializer
from home.models import ContractWithSpeaker, Course, Discount, DiscountAmount, ReferalValue, RegBonus, Users
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from backoffice.permissions import OwnerPermission, ManagerPermission
from home.serializers import ContractWithSpeakerSerializer, DjangoUserSerializers, RegBonusSerializer
from django.db.models import Q

# spikerlar ulushi
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | ManagerPermission])
def speaker_contract_edit(request):
    if request.method == 'GET':
        speaker_contract = ContractWithSpeaker.objects.last()
        serializer = ContractWithSpeakerSerializer(
            speaker_contract)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data
        contract = ContractWithSpeaker.objects.last()
        if contract is None:
            ContractWithSpeaker.objects.create(
                eduon=data['eduon']
            )
        else:
            contract.eduon = data['eduon']
            contract.save()
        return JsonResponse({'status': 'ok'})


# Reg bonus
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | ManagerPermission])
def reg_bonus_edit(request):
    if request.method == 'GET':
        reg_bonus = RegBonus.objects.last()
        serializer = RegBonusSerializer(
            reg_bonus)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data
        reg_bonus = RegBonus.objects.last()
        if reg_bonus is None:
            RegBonus.objects.create(
                summa=data['summa'],
                summa_full=data['summa_full']
            )
        else:
            reg_bonus.summa = data['summa']
            reg_bonus.summa_full = data['summa_full']
            reg_bonus.save()
        return JsonResponse({'status': 'ok'})


# Referal bonus
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | ManagerPermission])
def ref_bonus_edit(request):
    if request.method == 'GET':
        ref_bonus = ReferalValue.objects.last()
        serializer = ReferalValueSerializer(
            ref_bonus)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data
        ref_bonus = ReferalValue.objects.last()
        if ref_bonus is None:
            ReferalValue.objects.create(
                user_value=data['user_value'],
                speaker_value=data['speaker_value']
            )
        else:
            ref_bonus.user_value = data['user_value']
            ref_bonus.speaker_value = data['speaker_value']
            ref_bonus.save()
        return JsonResponse({'status': 'ok'})


# Referal bonus
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | ManagerPermission])
def set_discount_course(request):
    data = request.data
    course = data['course']
    discount = data['discount']
    course = Course.objects.get(id=course)
    course.discount = discount
    course.save()
    return JsonResponse({'status': course.name + ' discount set to ' + str(course.discount)})


# Search users to give bonus
@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def search_user(request):
    try:
        search = request.GET.get('q')
        if search is None:
            search = ""
        query = Users.objects.filter(Q(first_name__icontains=search) | Q(
            last_name__icontains=search) | Q(phone__contains=search) | Q(email__contains=search))

        serializer = DjangoUserSerializers(query, many=True)
        data = {
            "success": True,
            "error": "",
            "message": "Userlar olindi!",
            "data_courses": serializer.data,
        }

    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


# Give bonus to user
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | ManagerPermission])
def give_bonus(request):
    data = request.data
    user_id = data['user_id']
    bonus = data['bonus']
    print(bonus)
    user = Users.objects.get(id=user_id)
    user.bonus += int(bonus)
    user.save()
    return JsonResponse({'status': 'ok'})


# Get default discount amount
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | ManagerPermission])
def get_default_discount_amount(request):
    discount = DiscountAmount.objects.last()
    if discount:
        data = {
            'discount': discount.amount
        }
    else:
        data = {
            'discount': 'Belgilanmagan!'
        }
    
    return Response(data)


# Change course discount default amount
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | ManagerPermission])
def change_course_discount(request):
    discount = DiscountAmount.objects.last()
    if discount is not None:
        discount.amount = request.data['amount']
        discount.save()
    else:
        DiscountAmount.objects.create(amount=request.data['amount'])
    
    return Response({'status': 'ok'})


# delete discounts
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | ManagerPermission])
def delete_discounts(request):
    discounts = request.POST.getlist("discounts")
    items_map = map(int, discounts)
    items_int = list(items_map)
    
    for discount_id in items_int:
        discount = Discount.objects.get(id=discount_id)
        discount.course.discount = 0
        discount.course.save()
        discount.delete()
    
    return Response({'status': 'ok'})