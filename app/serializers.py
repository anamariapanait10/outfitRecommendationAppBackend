from rest_framework import serializers
from .models import OutfitItem

class OutfitItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutfitItem
        fields = '__all__'
        