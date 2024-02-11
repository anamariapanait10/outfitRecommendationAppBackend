from django.contrib.auth.models import User
from outfitRecommendationAppBackend.models import OutfitItem, Wardrobe
from rest_framework import permissions, serializers, viewsets, status
from rest_framework.response import Response


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

class OutfitItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutfitItem
        fields = '__all__'
        
class WardrobeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wardrobe
        fields = '__all__'

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
class OutfitItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows outfit items to be viewed or edited.
    """

    queryset = OutfitItem.objects.all()
    serializer_class = OutfitItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    

class WardrobeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows wardrobes to be viewed or edited.
    """

    queryset = Wardrobe.objects.all()
    serializer_class = WardrobeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Accessing serializer errors here
            print(serializer.errors)  # Example of printing errors to the console
            # You could log these errors, handle them, or customize the response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # If the data is valid, proceed with creation
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)