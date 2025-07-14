from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from firebase_messaging import sendPrivateMessage
from permissions import BanPermission, VerificationPermission
from products.models import Product

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


def _createMessage(conversation, message, image, second_user, first_user):
    ### TODO SEND FCM
    try:
        ## TODO: CHANGE THIS TO FIRST_USER
        sendPrivateMessage(
            reciever_user=first_user,
            message=message,
            conversation_id=conversation.id,
        )
        Message.objects.create(
            conversation=conversation,
            text=message,
            image=image,
            sender=second_user,
        )

        return Response({"detail": "تم إرسالة الرسالة بنجاح."})
    except:
        return Response(
            {"detail": "حدث خطأ ما."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def getConversations(request):
    user = request.user
    conversations = user.sender.all().union(user.receiver.all())
    conversation_serializer = ConversationSerializer(conversations, many=True)

    return Response(conversation_serializer.data)


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def getMessages(request):
    user = request.user
    conversation_id = request.query_params.get("conversation_id")

    conversation = Conversation.objects.get(id=conversation_id)

    if conversation.first_person != user and conversation.second_person != user:
        return Response(
            {"detail": "لا يمكنك الوصول إلى هذه المحادثة."},
            status=status.HTTP_403_FORBIDDEN,
        )
    messages: QuerySet = conversation.messages.all()

    serializer = MessageSerializer(messages, many=True, context={"user_id": user.id})
    return Response(serializer.data)

    # product = Product.objects.get(id=productPK)
    # ## PRODUCT'S SELLER
    # first_user = product.seller
    # ## CHATTER PERSON
    # second_user = request.user

    # try:
    #     try:
    #         conversation = Conversation.objects.get(
    #             first_person=first_user, second_person=second_user, product=product
    #         )

    #     except Conversation.DoesNotExist:
    #         conversation = Conversation.objects.get(
    #             first_person=second_user, second_person=first_user, product=product
    #         )

    # except Conversation.DoesNotExist:
    #     return Response([])


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def sendMessage(request):
    conversation_id = request.query_params.get("conversation_id", None)
    product_id = request.data.get("product_id")
    message = request.data.get("message")
    image = request.data.get("image", None)
    sender_user = request.user

    if conversation_id is not None:
        conversation = Conversation.objects.get(id=conversation_id)
        if conversation.first_person.id == sender_user.id:
            first_user = conversation.second_person
        else:
            first_user = conversation.first_person

        return _createMessage(
            conversation=conversation,
            image=image,
            second_user=sender_user,
            message=message,
            first_user=first_user,
        )

    else:
        product = Product.objects.get(id=product_id)
        ## PRODUCT'S SELLER
        first_user = product.seller

        try:
            try:
                conversation = Conversation.objects.get(
                    first_person=first_user, second_person=sender_user, product=product
                )
            except Conversation.DoesNotExist:
                conversation = Conversation.objects.get(
                    first_person=sender_user, second_person=first_user, product=product
                )

            return _createMessage(
                conversation=conversation,
                image=image,
                second_user=sender_user,
                message=message,
                first_user=first_user,
            )

        except Conversation.DoesNotExist:
            Conversation.objects.create(
                first_person=first_user, second_person=sender_user, product=product
            )

            return _createMessage(
                conversation=conversation,
                image=image,
                second_user=sender_user,
                message=message,
                first_user=first_user,
            )
