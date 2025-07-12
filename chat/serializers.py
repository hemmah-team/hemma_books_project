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

        x = {
            "conversation_id": tmp["id"],
            "product_id": tmp["product"]["id"],
            "product_name": tmp["product"]["name"],
        }

        return x


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ["conversation"]

    def to_representation(self, instance):
        initial = super().to_representation(instance)
        user_id = self.context.get("user_id")
        if user_id == initial.get("sender"):
            initial.pop("sender")
        return initial
