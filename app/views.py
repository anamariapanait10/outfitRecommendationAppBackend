import base64
from django.contrib.auth.models import User
from django.db.models import Prefetch
from app.models import ItemProbability, MarketplaceItems, OutfitItem, Wardrobe, WornOutfits
from rest_framework import permissions, serializers, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
import clothesFeatureExtraction.clothes_recognition_module as ai_model
from openai import OpenAI
import json

client = OpenAI()

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
        
class MarketplaceItemsSerializer(serializers.ModelSerializer):
    outfit = OutfitItemSerializer()
    class Meta:
        model = MarketplaceItems
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
        # category_mappings = {'Upper body clothes': 'Topwear', 'Lower body clothes': 'Bottomwear', 'Shoes': 'Footwear', 'Full body clothes': 'Bodywear', 'Head clothes': 'Headwear', 'Accessory': 'Accessories'}
        # # category = ai_model.classify_category_from_b64(request.data['image'])
        # category = category_mappings[ai_model.use_clip(['Upper body clothes', 'Lower body clothes', 'Shoes', 'Full body clothes', 'Head clothes', 'Accessory'], request.data['image'])]
        
        # subcategory = ai_model.classify_subcategory_from_b64(request.data['image'], category)
        # color = ai_model.classify_color_from_b64(request.data['image'])
        color  = ai_model.use_clip([
            'white', 'beige', 'black', 
            'light gray', 'gray', 'dark gray', 
            'yellow',  'dark yellow',  
            'light green', 'green', 'dark green', 
            'turquoise',  'orange',
            'light blue', 'blue', 'dark blue',  
            'light pink', 'pink', 'red',
            'dark red', 'brown', 'purple', 'multicolor'
        ], request.data['image'])
        print(f"color = {color}")
        # season = ai_model.classify_season_from_b64(request.data['image'])
        # usage = ai_model.classify_usage_from_b64(request.data['image'])
        subcategory = ai_model.use_clip(['Shirt', 'Tshirt', 'Sweater', 'Jacket', 'Jeans', 'Track Pants', 'Shorts', 'Skirt',
                                          'Trousers', 'Leggings', 'Casual Shoes', 'Flip Flops', 'Sandals', 'Formal Shoes', 'Flats', 
                                          'Sports Shoes', 'Heels', 'Tie', 'Watch', 'Belt', 'Jewelry'], request.data['image'])
        subcategory_mappings = { 'Shirt': 'Topwear', 'Tshirt': 'Topwear', 'Sweater': 'Topwear' , 'Jacket': 'Topwear', 'Jeans': 'Bottomwear', 'Track Pants': 'Bottomwear', 'Shorts': 'Bottomwear', 'Skirt': 'Bottomwear',
                                          'Trousers': 'Bottomwear', 'Leggings': 'Bottomwear', 'Casual Shoes': 'Footwear', 'Flip Flops': 'Footwear', 'Sandals': 'Footwear', 'Formal Shoes': 'Footwear', 'Flats': 'Footwear',
                                          'Sports Shoes': 'Footwear', 'Heels': 'Footwear', 'Tie': 'Accessories', 'Watch': 'Accessories', 'Belt': 'Accessories', 'Jewelry': 'Accessories' }
        category = subcategory_mappings[subcategory]
        season = ai_model.use_clip(['Spring clothes', 'Summer clothes', 'Autumn clothes', 'Winter clothes'], request.data['image'])
        usage = ai_model.use_clip(['Casual clothes', 'Ethnic clothes', 'Formal clothes', 'Sports clothes', 'Smart casual clothes', 'Party clothes'],  request.data['image'])
        season = season[:season.find(' clothes')]
        usage = usage[:usage.find(' clothes')]
        json = {"category": category, "subcategory": subcategory, "color": color, "season": season, "occasions": usage}
        print(f"json = {json}")
        return Response(data=json, status=status.HTTP_200_OK)
    
    def load_img_base64(self, path):
        with open(path, "rb") as f:
            encoded_image = base64.b64encode(f.read())
        return encoded_image
        
    @action(detail=False, methods=['get'])
    def get_recommendations(self, request):
        topwear = OutfitItem.objects.all().filter(category='topwear')
        bottomwear = OutfitItem.objects.all().filter(category='bottomwear')
        footwear = OutfitItem.objects.all().filter(category='footwear')
        
        weather = request.query_params['weather']
        temperature = request.query_params['temperature']
        print(f"weather {weather}")
        print(f"temperature {temperature}")
        
        recommendations = []

        if len(topwear) > 0:
            print("topwear")
            topwearPercentages = []
            for item in topwear:
                topwearPercentages.append(float(getattr(ItemProbability.objects.filter(outfitItem=item.id).first(), weather + temperature)))
            print("topwear probs before normalization ", topwearPercentages)
            topwearPercentages = ai_model.normalize_percentages(topwearPercentages)
            print("topwear probs after normalization ", topwearPercentages)
            print("p / 100 ", [p / 100 for p in topwearPercentages])
            topwearProbabilities = []
            for percentage in topwearPercentages:
                likelihood = percentage / 100.0
                prior = 1.0 / len(topwear)
                marginal = likelihood * prior + (1-likelihood) * (1-prior)
                posterior = likelihood * prior / marginal
                print(f"prior {prior}, marginal {marginal}, posterior {posterior}")
                topwearProbabilities.append(posterior)
            print("topwear prob ", topwearProbabilities)
            selected_topwear = topwear[topwearPercentages.index(max(topwearPercentages))]
            recommendations.append({ "id": selected_topwear.id, "image": selected_topwear.image})
        else:
            recommendations.append({"id": -1, "image": "data:image/png;base64," + self.load_img_base64(r'app\assets\question_mark.png').decode('utf-8')})

        if len(bottomwear) > 0:
            print("bottomwear")
            bottomwearPercentages = []
            for item in bottomwear:
                bottomwearPercentages.append(float(getattr(ItemProbability.objects.filter(outfitItem=item.id).first(), weather + temperature)))
            print("bottomwear probs before normalization ", bottomwearPercentages)
            bottomwearPercentages = ai_model.normalize_percentages(bottomwearPercentages)
            print("bottomwear prob after normalization", bottomwearPercentages)
            print("p / 100 ", [p / 100 for p in bottomwearPercentages])
            bottomwearProbabilities = []
            for percentage in bottomwearPercentages:
                likelihood = percentage / 100.0
                prior = 1.0 / len(bottomwear)
                marginal = likelihood * prior + (1-likelihood) * (1-prior)
                posterior = likelihood * prior / marginal
                print(f"prior {prior}, marginal {marginal}, posterior {posterior}")
                bottomwearProbabilities.append(posterior)
            print("bottomwear prob ", bottomwearProbabilities)
            selected_bottomwear = bottomwear[bottomwearProbabilities.index(max(bottomwearProbabilities))]
            print(selected_bottomwear.image[:30])
            recommendations.append({ "id": selected_bottomwear.id, "image": selected_bottomwear.image})
        else:
            recommendations.append({"id": -2, "image": "data:image/png;base64," + self.load_img_base64(r'app\assets\question_mark.png').decode('utf-8')})
        
        if len(footwear) > 0:
            print("footwear")
            footwearPercentages = []
            for item in footwear:
                footwearPercentages.append(float(getattr(ItemProbability.objects.filter(outfitItem=item.id).first(), weather + temperature)))
            print("footwear probs before normalization ", footwearPercentages)
            footwearPercentages = ai_model.normalize_percentages(footwearPercentages)
            print("footwear probs after normalization ", footwearPercentages)
            print("p / 100 ", [p / 100 for p in footwearPercentages])
            footwearProbabilities = []
            for percentage in bottomwearPercentages:
                likelihood = percentage / 100.0
                prior = 1.0 / len(footwear)
                marginal = likelihood * prior + (1-likelihood) * (1-prior)
                posterior = likelihood * prior / marginal
                print(f"prior {prior}, marginal {marginal}, posterior {posterior}")
                footwearProbabilities.append(posterior)
            print("footwear prob ", footwearProbabilities)
            selected_footwear = footwear[footwearPercentages.index(max(footwearPercentages))]
            recommendations.append({ "id": selected_footwear.id, "image": selected_footwear.image})
        else:
            recommendations.append({"id": -3, "image": "data:image/png;base64," + self.load_img_base64(r'app\assets\question_mark.png').decode('utf-8')})

        return Response(data=recommendations, status=status.HTTP_200_OK)

class WardrobeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows wardrobes to be viewed or edited.
    """

    queryset = Wardrobe.objects.all()
    serializer_class = WardrobeSerializer
    permission_classes = [permissions.IsAuthenticated]

class WornOutfitsViewSet(viewsets.ModelViewSet):
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
    
class MarketplaceItemsViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceItems.objects.all()
    serializer_class = MarketplaceItemsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def get_available_items_for_user(self, request):
        user = request.query_params['userId']
        availableItems = MarketplaceItems.objects.prefetch_related('outfit').filter(user_id=user)
        result = []
        for item in availableItems:
            serializer = MarketplaceItemsSerializer(item)
            result.append(serializer.data)

        return Response(result)

class AiExpertViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def ask(self, request):
        topwear_image = request.data['topwear']['image']
        bottomwear_image = request.data['bottomwear']['image']
        footwear_image = request.data['footwear']['image']
        event = request.data['event']
        if topwear_image == None or bottomwear_image == None or footwear_image == None:
            return Response('Bad request', status=status.HTTP_400_BAD_REQUEST)
        if not event:
            prompt = "Here are images of the selected outfit. Based on their style, color, material, and overall appearance, can these clothes be combined and look great? Return in JSON with decision and reason. Keep the reason shorter than 140 tokens"
        else:
            prompt = f"Here are images of the selected outfit. Based on their style, color, material, overall appearance and the suitability for a {event.lower()} occasion, can these clothes be combined and look great? Return in JSON with decision and reason. Keep the reason shorter than 140 tokens"
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": topwear_image,
                            "detail": "low"
                        },
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": bottomwear_image,
                            "detail": "low"
                        },
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":footwear_image,
                            "detail": "low"
                        },
                    },
                ],
                }
            ],
            max_tokens=150,
        )

        # try:
        #     with open('raspuns.json', 'r') as f:
        #         # f.write(response.choices[0].message.content)
        #         response = f.read()
        #         f.close()
        # except Exception as e:
        #     print(e)
        # response = response.choices[0].message.content
        response = json.loads(response.replace('```json', '').replace('```', ''))
        # print(response)
        return Response(response)
