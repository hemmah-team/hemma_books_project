from django.db.models.query import QuerySet
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions import BanPermission, VerificationPermission
from products.models import Product

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


def _createMessage(conversation, message, image, second_user):
    Message.objects.create(
        conversation=conversation, text=message, image=image, sender=second_user
    )

    return Response({"detail": "تم إرسالة الرسالة بنجاح."})


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def getConversations(request):
    user = request.user
    conversations = user.sender.all().union(user.receiver.all())
    ser = ConversationSerializer(conversations, many=True)
    return Response(ser.data)


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def getMessages(request, productPK):
    product = Product.objects.get(id=productPK)
    ## PRODUCT'S SELLER
    first_user = product.seller
    ## CHATTER PERSON
    second_user = request.user

    try:
        try:
            conversation = Conversation.objects.get(
                first_person=first_user, second_person=second_user, product=product
            )

        except Conversation.DoesNotExist:
            conversation = Conversation.objects.get(
                first_person=second_user, second_person=first_user, product=product
            )

        messages: QuerySet = conversation.messages.all()

        serializer = MessageSerializer(
            messages, many=True, context={"user_id": second_user.id}
        )
        return Response(serializer.data)
    except Conversation.DoesNotExist:
        return Response([])


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def sendMessage(request):
    product_id = request.data.get("product_id")
    message = request.data.get("message")
    image = request.data.get("image", None)
    product = Product.objects.get(id=product_id)
    ## PRODUCT'S SELLER
    first_user = product.seller
    ## CHATTER PERSON
    second_user = request.user

    try:
        try:
            conversation = Conversation.objects.get(
                first_person=first_user, second_person=second_user, product=product
            )
        except Conversation.DoesNotExist:
            conversation = Conversation.objects.get(
                first_person=second_user, second_person=first_user, product=product
            )

        return _createMessage(
            conversation=conversation,
            image=image,
            second_user=second_user,
            message=message,
        )

    except Conversation.DoesNotExist:
        Conversation.objects.create(
            first_person=first_user, second_person=second_user, product=product
        )

        return _createMessage(
            conversation=conversation,
            image=image,
            second_user=second_user,
            message=message,
        )
