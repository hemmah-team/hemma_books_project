from rest_framework import serializers

from products.serializers import MostBasicProductSerializer

from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    product = MostBasicProductSerializer()

    class Meta:
        model = Conversation
        fields = ["id", "product"]

    def to_representation(self, instance):
        tmp = super().to_representation(instance)
        message = instance.messages.all().order_by("-created_at")[0]
        print(f"tmp is is {tmp}")
        message = message.text
        ## TODO: HERE WILL RESULT IN ERROR IF PRODUCT IS DELETED
        x = {
            "conversation_id": tmp["id"],
            "product_id": tmp["product"]["id"],
            "product_name": tmp["product"]["name"],
            "last_message": str(message),
        }

        return x


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ["conversation"]

    def to_representation(self, instance):
        from_support = instance.conversation.support
        initial = super().to_representation(instance)

        user_id = self.context.get("user_id")
        if user_id == initial.get("sender"):
            initial.pop("sender")
        if from_support is True and initial.get("sender", None) is not None:
            initial["sender"] = 0
        return initial
