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

        return Response(
            {"conversation_id": conversation.id, "product_id": conversation.product.id}
        )
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
    ## TODO: THIS IS NOT FULL, NEEDS FIXING
    conversations = (user.chatter.all()).filter(support=False)

    ## !! START OF TEST
    products = Product.objects.filter(seller=user)
    for product in products:
        conversations = conversations.union(product.product_chatter.all())

    ## !! END OF TEST
    conversation_serializer = ConversationSerializer(conversations, many=True)

    return Response(conversation_serializer.data)


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def getMessages(request):
    user = request.user
    conversation_id = request.query_params.get("conversation_id", None)
    product_id = request.query_params.get("product_id", None)
    for_support = request.query_params.get("support", None)

    if for_support:
        try:
            conversation = Conversation.objects.get(chatter=user, support=True)

        except Conversation.DoesNotExist:
            return Response([])

    else:
        if conversation_id is not None:
            conversation = Conversation.objects.get(id=conversation_id)

            if conversation.chatter != user and conversation.product.seller != user:
                return Response(
                    {"detail": "لا يمكنك الوصول إلى هذه المحادثة."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        else:
            product = Product.objects.get(id=product_id)
            try:
                conversation = Conversation.objects.get(product=product, chatter=user)
            except Conversation.DoesNotExist:
                return Response([])

    messages: QuerySet = conversation.messages.all()
    serializer = MessageSerializer(messages, many=True, context={"user_id": user.id})
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def sendMessage(request):
    conversation_id = request.query_params.get("conversation_id", None)
    product_id = request.query_params.get("product_id", None)
    message = request.data.get("message")
    image = request.data.get("image", None)
    sender_user = request.user

    if conversation_id is not None:
        conversation = Conversation.objects.get(id=conversation_id)
        if conversation.chatter.id == sender_user.id:
            first_user = conversation.product.seller
        else:
            first_user = sender_user

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
            conversation = Conversation.objects.get(
                chatter=sender_user, product=product
            )

            return _createMessage(
                conversation=conversation,
                image=image,
                second_user=sender_user,
                message=message,
                first_user=first_user,
            )

        except Conversation.DoesNotExist:
            ################## !!!! HERE CONVERSATION DOES NOT EXIST ############
            ################## !!!! REQUEST USER IS CHATTER #####################
            conversation = Conversation.objects.create(
                chatter=sender_user, product=product
            )

            return _createMessage(
                conversation=conversation,
                image=image,
                second_user=sender_user,
                message=message,
                first_user=first_user,
            )
