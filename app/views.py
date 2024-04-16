from django.contrib.auth.models import User
from django.db.models import Prefetch
from app.models import ItemProbability, OutfitItem, Wardrobe, WornOutfits
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
        
class WornOutfitsSerializer(serializers.ModelSerializer):
    top = OutfitItemSerializer()
    bottom = OutfitItemSerializer()
    shoes = OutfitItemSerializer()

    class Meta:
        model = WornOutfits
        fields = ['date', 'user_id', 'top', 'bottom', 'shoes']
        
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
        
        sunnyHot = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 40, 6), ai_model.calc_wear_probability(weather, 30, 6)), 2)
        sunnyMild = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 15, 6), ai_model.calc_wear_probability(weather, 30, 6)), 2)
        sunnyCold = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, -10, 6), ai_model.calc_wear_probability(weather, 30, 6)), 2)
        overcastHot = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 40, 6), ai_model.calc_wear_probability(weather, 20, 6)), 2)
        overcastMild = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 15, 6), ai_model.calc_wear_probability(weather, 20, 6)), 2)
        overcastCold = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, -10, 6), ai_model.calc_wear_probability(weather, 20, 6)), 2)
        rainyHot = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 40, 6), ai_model.calc_wear_probability(weather, 10, 6)), 2)
        rainyMild = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 15, 6), ai_model.calc_wear_probability(weather, 10, 6)), 2)
        rainyCold = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, -10, 6), ai_model.calc_wear_probability(weather, 10, 6)), 2)
        snowyHot = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 40, 6), ai_model.calc_wear_probability(weather, 0, 6)), 2)
        snowyMild = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, 15, 6), ai_model.calc_wear_probability(weather, 0, 6)), 2)
        snowyCold = round(100 * ai_model.calc_mean(ai_model.calc_wear_probability(temperature, -10, 6), ai_model.calc_wear_probability(weather, 0, 6)), 2)
        
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
        
        ItemProbability.objects.create(
            outfitItem=OutfitItem.objects.filter(id=serializer.data['id']).first(), 
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
            snowyCold=snowyCold
        )
        
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
        topwear = OutfitItem.objects.all().filter(category='topwear')
        bottomwear = OutfitItem.objects.all().filter(category='bottomwear')
        footwear = OutfitItem.objects.all().filter(category='footwear')
        
        weather = request.query_params['weather']
        temperature = request.query_params['temperature']
        
        def probabilitiesNormalization(weatherAndTemperatureName):
            weatherAndTemperatureList = list(ItemProbability.objects.values_list(weatherAndTemperatureName, flat=True))
            normalizedList = ai_model.normalize_percentages(weatherAndTemperatureList)
            return normalizedList

        recommendations = []
 
        topwearProbabilities = []
        for item in topwear:
            probabilitiesNormalization(weatherAndTemperatureName=weather + temperature)
            topwearProbabilities.append(ItemProbability.objects.filter(outfitItem=item.id)[weather + temperature] * 1 / len(topwear) * 1 / 12)
        recommendations.append(topwear[topwearProbabilities.index(max(topwearProbabilities))])
        
        bottomwearProbabilities = []
        for item in bottomwear:
            bottomwearProbabilities.append(ItemProbability.objects.filter(outfitItem=item.id)[weather + temperature] * 1 / len(bottomwear) * 1 / 12)
        recommendations.append(bottomwear[bottomwearProbabilities.index(max(bottomwearProbabilities))])
            
        footwearProbabilities = []
        for item in footwear:
            footwearProbabilities.append(ItemProbability.objects.filter(outfitItem=item.id)[weather + temperature] * 1 / len(footwear) * 1 / 12)
        recommendations.append(footwear[footwearProbabilities.index(max(footwearProbabilities))])
        
        return Response(data=recommendations, status=status.HTTP_200_OK)

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
    

class WornOutfitsViewSet(viewsets.ViewSet):
    queryset = WornOutfits.objects.all()
    serializer_class = WornOutfitsSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_for_year_month(self, request):
        wornOutfits = WornOutfits.objects.prefetch_related('top', 'bottom', 'shoes').filter(user_id=request.user).filter(date__startswith=request.query_params['yearMonth'])
        result = {}
        for item in wornOutfits:
            serializer = WornOutfitsSerializer(item)
            result[item.date] = serializer.data
        
        return Response(result)
    

    @action(detail=False, methods=['post'])
    def wear(self, request):
        outfitItems = request.data['outfit']
        date = request.data['date']
        top = next((obj for obj in outfitItems if obj.category == "Topwear"), None)
        bottom = next((obj for obj in outfitItems if obj.category == "Bottomwear"), None)
        shoes = next((obj for obj in outfitItems if obj.category == "Shoes"), None)

        WornOutfits.objects.create(date=date, user=request.user, top=top, bottom=bottom, shoes=shoes)

        return Response(status=status.HTTP_200_OK)