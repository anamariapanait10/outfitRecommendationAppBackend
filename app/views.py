from django.contrib.auth.models import User
from app.models import OutfitItem, Wardrobe
from rest_framework import permissions, serializers, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
import clothesFeatureExtraction.clothes_recognition_module as ai_model

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
    
    def create(self, request, *args, **kwargs):
        wardrobe_id = None
        if Wardrobe.objects.filter(user_id=request.user).exists():
            wardrobe_id = Wardrobe.objects.filter(user_id=request.user).first().id
        else:
            print("This user does not have a wardrobe yet, so it will be created now.")
            wardrobe_id = Wardrobe.objects.create(user_id=request.user).id

        request.data['wardrobe'] = wardrobe_id
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Accessing serializer errors here
            print(serializer.errors)  # Example of printing errors to the console
            print("Serialization errors")
            # You could log these errors, handle them, or customize the response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # If the data is valid, proceed with creation
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.queryset.filter(wardrobe_id=Wardrobe.objects.filter(user_id=request.user).first().id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def classify(self, request):
        category = ai_model.classify_category_from_b64(request.data['image'])
        subcategory = ai_model.classify_subcategory_from_b64(request.data['image'])
        color = ai_model.classify_color_from_b64(request.data['image'])
        season = ai_model.classify_season_from_b64(request.data['image'])
        usage = ai_model.classify_usage_from_b64(request.data['image'])
        json = {"category": category, "subcategory": subcategory, "color": color, "season": season, "occasions": usage}
        print(f"json = {json}")
        return Response(data=json, status=status.HTTP_200_OK)

class WardrobeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows wardrobes to be viewed or edited.
    """

    queryset = Wardrobe.objects.all()
    serializer_class = WardrobeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     if not serializer.is_valid():
    #         # Accessing serializer errors here
    #         print(serializer.errors)  # Example of printing errors to the console
    #         print("erori la serializare")
    #         # You could log these errors, handle them, or customize the response
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    #     # If the data is valid, proceed with creation
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class ClassificationViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def classify(self, request):
        return Response('Hello World')