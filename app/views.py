from django.contrib.auth.models import User
from app.models import ItemProbability, OutfitItem, Wardrobe
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
        
class ItemProbabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemProbability
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
        # check if the user already 
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
        temperature = request.data['temperature'] # temperatura intre -10 si 40 grade
        weather = request.data['weather'] # nr intre 0 si 30
        
        sunnyHot = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 40, 6), ai_model.calc_wear_probability(weather, 30, 6))
        sunnyMild = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 15, 6), ai_model.calc_wear_probability(weather, 30, 6))
        sunnyCold = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, -10, 6), ai_model.calc_wear_probability(weather, 30, 6))
        overcastHot = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 40, 6), ai_model.calc_wear_probability(weather, 20, 6))
        overcastMild = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 15, 6), ai_model.calc_wear_probability(weather, 20, 6))
        overcastCold = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, -10, 6), ai_model.calc_wear_probability(weather, 20, 6))
        rainyHot = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 40, 6), ai_model.calc_wear_probability(weather, 10, 6))
        rainyMild = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 15, 6), ai_model.calc_wear_probability(weather, 10, 6))
        rainyCold = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, -10, 6), ai_model.calc_wear_probability(weather, 10, 6))
        snowyHot = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 40, 6), ai_model.calc_wear_probability(weather, 0, 6))
        snowyMild = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 15, 6), ai_model.calc_wear_probability(weather, 0, 6))
        snowyCold = 100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, -10, 6), ai_model.calc_wear_probability(weather, 0, 6))
        
        print("sunnyHot = ", format(sunnyHot, '.2f'))
        print("sunnyMild = ", format(sunnyMild, '.2f'))
        print("sunnyCold = ", format(sunnyCold, '.2f'))
        print("overcastHot = ", format(overcastHot, '.2f'))
        print("overcastMild = ", format(overcastMild, '.2f'))
        print("overcastCold = ", format(overcastCold, '.2f'))
        print("rainyHot = ", format(rainyHot, '.2f'))
        print("rainyMild = ", format(rainyMild, '.2f'))
        print("rainyCold = ", format(rainyCold, '.2f'))
        print("snowyHot = ", format(snowyHot, '.2f'))
        print("snowyMild = ", format(snowyMild, '.2f'))
        print("snowyCold = ", format(snowyCold, '.2f'))
        
        sunnyHotList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('sunnyHot', flat=True)).append(sunnyHot))
        sunnyHot = sunnyHotList[-1]
        ItemProbability.objects.bulk_update(sunnyHotList[:-1], ['sunnyHot'])
        
        sunnyMildList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('sunnyMild', flat=True)).append(sunnyMild))
        sunnyMild = sunnyMildList[-1]
        ItemProbability.objects.bulk_update(sunnyMildList[:-1], ['sunnyMild'])
        
        sunnyColdList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('sunnyCold', flat=True)).append(sunnyCold))
        sunnyCold = sunnyColdList[-1]
        ItemProbability.objects.bulk_update(sunnyColdList[:-1], ['sunnyCold'])
        
        overcastHotList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('overcastHot', flat=True)).append(overcastHot))
        overcastHot = overcastHotList[-1]
        ItemProbability.objects.bulk_update(overcastHotList[:-1], ['overcastHot'])
        
        overcastMildList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('overcastMild', flat=True)).append(overcastMild))
        overcastMild = overcastMildList[-1]
        ItemProbability.objects.bulk_update(overcastMildList[:-1], ['overcastMild'])
        
        overcastColdList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('overcastCold', flat=True)).append(overcastCold))
        overcastCold = overcastColdList[-1]
        ItemProbability.objects.bulk_update(overcastColdList[:-1], ['overcastCold'])
        
        rainyHotList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('rainyHot', flat=True)).append(rainyHot))
        rainyHot = rainyHotList[-1]
        ItemProbability.objects.bulk_update(rainyHotList[:-1], ['rainyHot'])
        
        rainyMildList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('rainyMild', flat=True)).append(rainyMild))
        rainyMild = rainyMildList[-1]
        ItemProbability.objects.bulk_update(rainyMildList[:-1], ['rainyMild'])
        
        rainyColdList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('rainyCold', flat=True)).append(rainyCold))
        rainyCold = rainyColdList[-1]
        ItemProbability.objects.bulk_update(rainyColdList[:-1], ['rainyCold'])
        
        snowyHotList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('snowyHot', flat=True)).append(snowyHot))
        snowyHot = snowyHotList[-1]
        ItemProbability.objects.bulk_update(snowyHotList[:-1], ['snowyHot'])
        
        snowyMildList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('snowyMild', flat=True)).append(snowyMild))
        snowyMild = snowyMildList[-1]
        ItemProbability.objects.bulk_update(snowyMildList[:-1], ['snowyMild'])
        
        snowyColdList = ai_model.normalize_percentages(list(ItemProbability.objects.values_list('snowyCold', flat=True)).append(snowyCold))
        snowyCold = snowyColdList[-1]
        ItemProbability.objects.bulk_update(snowyColdList[:-1], ['snowyCold'])
        
        ItemProbability.objects.create(outfitItem=serializer.data.id,
                                       sunnyHot=sunnyHot,
                                       sunnyMild=sunnyMild,
                                       sunnyCold=sunnyCold,
                                       overcastHot=overcastHot,
                                       overcastMild=overcastMild,
                                       overcastCold=overcastCold,
                                       rainyHot=rainyHot,
                                       rainyMild=rainyMild,
                                       rainyCold=rainyCold,
                                       snowyHot=snowyHot,
                                       snowyMild=snowyMild,
                                       snowyCold=snowyCold)
        
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
        subcategory = ai_model.classify_subcategory_from_b64(request.data['image'], category)
        color = ai_model.classify_color_from_b64(request.data['image'])
        season = ai_model.classify_season_from_b64(request.data['image'])
        usage = ai_model.classify_usage_from_b64(request.data['image'])
        json = {"category": category, "subcategory": subcategory, "color": color, "season": season, "occasions": usage}
        print(f"json = {json}")
        return Response(data=json, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def get_recommendations(self, request):
        
        pass

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