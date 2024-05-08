import base64
from django.contrib.auth.models import User
from django.db.models import Prefetch
from app.models import ItemProbability, MarketplaceItems, OutfitItem, Wardrobe, WornOutfits, Stats
from rest_framework import permissions, serializers, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
import clothesFeatureExtraction.clothes_recognition_module as ai_model
from openai import OpenAI
from datetime import date
import json
import numpy as np

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

class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stats
        fields = '__all__'

class WornOutfitsSerializer(serializers.ModelSerializer):
    top = OutfitItemSerializer()
    bottom = OutfitItemSerializer()
    shoes = OutfitItemSerializer()

    class Meta:
        model = WornOutfits
        fields = ['date', 'user', 'top', 'bottom', 'shoes']
        
class ItemProbabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemProbability
        fields = '__all__'

class MarketplaceItemReadSerializer(serializers.ModelSerializer):
    outfit = OutfitItemSerializer(read_only=True)

    class Meta:
        model = MarketplaceItems
        fields = '__all__'

class MarketplaceItemWriteSerializer(serializers.ModelSerializer):
    outfit = serializers.PrimaryKeyRelatedField(queryset=OutfitItem.objects.all())

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
        if Wardrobe.objects.filter(user_id=request.user).exists():
            wardrobe_id = Wardrobe.objects.filter(user_id=request.user).first().id
        else:
            wardrobe_id = Wardrobe.objects.create(user_id=request.user).id

        request.data['wardrobe'] = wardrobe_id
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        
        temperature = request.data['temperature'] # temperatura intre -10 si 40 grade
        weather = request.data['weather'] # vremea intre 0 si 30
    
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
        # category = ai_model.classify_category_from_b64(request.data['image'])        
        # subcategory = ai_model.classify_subcategory_from_b64(request.data['image'], category)
        # color = ai_model.classify_color_from_b64(request.data['image'])
        # season = ai_model.classify_season_from_b64(request.data['image'])
        # usage = ai_model.classify_usage_from_b64(request.data['image'])
        color = ai_model.use_clip([
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
        subcategory = ai_model.use_clip(['Shirt', 'Tshirt', 'Sweater', 'Jacket', 
                                         'Jeans', 'Track Pants', 'Shorts', 'Skirt', 'Trousers', 'Leggings', 
                                         'Sneakers', 'Flip Flops', 'Sandals', 'Flats', 'Sports Shoes', 'Heels',
                                         'Tie', 'Watch', 'Belt', 'Jewelry'], request.data['image'])
        subcategory_mappings = { 'Shirt': 'Topwear', 'Tshirt': 'Topwear', 'Sweater': 'Topwear' , 'Jacket': 'Topwear', 
                                 'Jeans': 'Bottomwear', 'Track Pants': 'Bottomwear', 'Shorts': 'Bottomwear', 'Skirt': 'Bottomwear', 'Trousers': 'Bottomwear', 'Leggings': 'Bottomwear', 
                                 'Sneakers': 'Footwear', 'Flip Flops': 'Footwear', 'Sandals': 'Footwear', 'Flats': 'Footwear', 'Sports Shoes': 'Footwear', 'Heels': 'Footwear', 
                                 'Tie': 'Accessories', 'Watch': 'Accessories', 'Belt': 'Accessories', 'Jewelry': 'Accessories' }
        category = subcategory_mappings[subcategory]
        season = ai_model.use_clip(['Spring clothes', 'Summer clothes', 'Autumn clothes', 'Winter clothes'], request.data['image'])
        season = season[:season.find(' clothes')]
        usage = ai_model.use_clip(['Casual clothes', 'Ethnic clothes', 'Formal clothes', 'Sports clothes', 'Smart Casual clothes', 'Party clothes'],  request.data['image'])
        usage = usage[:usage.find(' clothes')]
        material = ai_model.use_clip(['Cotton', 'Wool', 'Silk', 'Polyester', 'Nylon'], request.data['image'])
        pattern = ai_model.use_clip(['Striped', 'Checkered', 'Floral', 'Dotted', 'Plain'], request.data['image'])
        json = {"category": category, "subcategory": subcategory, "color": color, "season": season, "occasions": usage, "material": material, "pattern": pattern}
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
        print("-" * 49)
        print(f"weather = {weather}")
        print(f"temperature = {temperature}")
        
        recommendations = []

        for wear_category, category_name in [(topwear, "Topwear"), (bottomwear, "Bottomwear"), (footwear, "Footwear")]:
            if len(wear_category) > 0:
                print("-" * 20, category_name, "-" * 20)
                percentages = [float(getattr(ItemProbability.objects.filter(outfitItem=item.id).first(), weather + temperature)) for item in wear_category]
                probabilities = [p / 100 for p in percentages]
                print(f"{category_name} probs before normalization ", probabilities)
                probabilities = ai_model.normalize_probabilities(probabilities)
                print(f"{category_name} probs after normalization ", probabilities)
                
                print("\tprior\t\tmarginal\tlikelihood")
                new_probabilities = []
                for prob in probabilities:
                    likelihood = prob
                    prior = 1.0 / len(wear_category)
                    # marginal = likelihood * prior + (1-likelihood) * (1-prior)
                    marginal = sum(probabilities) * prior
                    posterior = likelihood * prior / marginal
                    print(f"{prior} {marginal} {likelihood}")
                    new_probabilities.append(posterior)
                
                print(f"{category_name} prob before normalization", new_probabilities)
                print("Sum of probabilities ", sum(new_probabilities))
                new_probabilities = ai_model.normalize_probabilities(new_probabilities)
                print(f"{category_name} prob after normalization", new_probabilities)
                print("Sum of probabilities ", sum(new_probabilities))
                random_variable = np.random.choice(len(new_probabilities), p=new_probabilities)
                print("Random variable ", random_variable)
                selected_item = wear_category[random_variable]
                recommendations.append({"id": selected_item.id, "image": selected_item.image, "category": selected_item.category})
            else:
                recommendations.append({"id": -1 if category_name == "topwear" else -2 if category_name == "bottomwear" else -3, "image": "data:image/png;base64," + self.load_img_base64(r'app\assets\question_mark.png').decode('utf-8')})
        print("-" * 49)
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
        wornOutfits = WornOutfits.objects.prefetch_related('top', 'bottom', 'shoes').filter(user=request.user).filter(date__startswith=request.query_params['yearMonth'])
        result = {}
        for item in wornOutfits:
            serializer = WornOutfitsSerializer(item)
            result[item.date] = serializer.data
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def wear(self, request):
        outfitItems = request.data['outfit']
        date = request.data['date']
        first = OutfitItem.objects.filter(id=outfitItems[0]['id']).first()
        second = OutfitItem.objects.filter(id=outfitItems[1]['id']).first()
        third = OutfitItem.objects.filter(id=outfitItems[2]['id']).first()
        outfitItems = [first, second, third]
        
        top = next((obj for obj in outfitItems if obj.category == "Topwear"), None)
        bottom = next((obj for obj in outfitItems if obj.category == "Bottomwear"), None)
        shoes = next((obj for obj in outfitItems if obj.category == "Footwear"), None)

        WornOutfits.objects.create(date=date, user=request.user, top=top, bottom=bottom, shoes=shoes)

        return Response(data="{}", status=status.HTTP_200_OK)
    
class MarketplaceItemsViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceItems.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return MarketplaceItemReadSerializer
        return MarketplaceItemWriteSerializer
    
    @action(detail=False, methods=['get'])
    def get_available_items_for_user(self, request):
        user = request.query_params['userId']
        availableItems = MarketplaceItems.objects.prefetch_related('outfit').filter(user_id=user)
        result = []
        for item in availableItems:
            serializer = MarketplaceItemReadSerializer(item)
            result.append(serializer.data)

        return Response(result)
    
    @action(detail=False, methods=['get'])
    def similarity(self, request):
        marketplace_item_id = request.query_params['marketplaceItemId']
        marketplace_item = MarketplaceItems.objects.prefetch_related('outfit').filter(id=marketplace_item_id).first()
        marketplace_items = MarketplaceItems.objects.prefetch_related('outfit').exclude(id=marketplace_item_id)
        similarity = ai_model.calculate_similarity(marketplace_item, marketplace_items)
        
        result = []
        for item in similarity:
            serializer = MarketplaceItemReadSerializer(item)
            result.append(serializer.data)
        
        return Response(data=result, status=status.HTTP_200_OK)

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
            prompt = (
                "Here are images of the selected outfit. Based on their style, color, material, and overall appearance, can these clothes be "
                "combined and look great? Return in JSON with decision and reason. Keep the reason shorter than 140 tokens"
            )
        else:
            prompt = (
                "Here are images of the selected outfit. Based on their style, color, material, overall appearance and the suitability "
                f"for a {event.lower()} occasion, can these clothes be combined and look great? Return in JSON with decision and reason. "
                "Keep the reason shorter than 140 tokens"
            )
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
        response = response.choices[0].message.content
        response = json.loads(response.replace('```json', '').replace('```', ''))
        # print(response)
        return Response(response)

class StatsViewSet(viewsets.ModelViewSet):
    queryset = Stats.objects.all()
    serializer_class = StatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def compute_wardrobe_usage(self, user):
        print("Compute wardrobe usage")
        latest = Stats.objects.filter(wardrobe__user_id=user).filter(is_latest=True).first()
        print("Latest ", latest)
        current_date = date.today()
        if not latest or latest.last_calculated.month != current_date.month:
            wardrobe = Wardrobe.objects.filter(user_id=user).first()
            print("Wardrobe ", wardrobe)
            month = current_date.month
            if month in range(3, 6):
                season = "Spring"
                start_date = date(current_date.year, 3, 1)
            elif month in range(6, 9):
                season = "Summer"
                start_date = date(current_date.year, 6, 1)
            elif month in range(9, 12):
                season = "Autumn"
                start_date = date(current_date.year, 9, 1)
            else:
                season = "Winter"
                start_date = date(current_date.year, 12, 1)
            print("Season ", season)
            print("Month ", month)
            total_seasonal_items = OutfitItem.objects.filter(wardrobe=wardrobe, seasons__contains=season).count()
            print("Total seasonal items ", total_seasonal_items)
            if total_seasonal_items == 0:
                return 0
            # get the ids of the items that were worn in the current season and that are designated for the current season
            worn_outfits_in_season = WornOutfits.objects.filter(user=user, date__gte=start_date)
            print("Worn outfits in season ", worn_outfits_in_season)
            worn_items_ids = []
            for outfit in worn_outfits_in_season:
                if season in outfit.top.seasons:
                    worn_items_ids.append(outfit.top_id)
                if season in outfit.bottom.seasons:
                    worn_items_ids.append(outfit.bottom_id)
                if season in outfit.shoes.seasons:
                    worn_items_ids.append(outfit.shoes_id)
            worn_items = len(list(set(worn_items_ids)))
            print("Worn items ", worn_items)
            worn_items_percentage = (worn_items / total_seasonal_items) * 100
            print("Worn items percentage ", worn_items_percentage)
            number_of_days_in_season = (current_date - start_date).days
            print("Number of days in season ", number_of_days_in_season)
            worn_outfits_percentage = (len(worn_outfits_in_season) / number_of_days_in_season) * 100
            Stats.objects.create(wardrobe=wardrobe, worn_clothes_percentage=worn_items_percentage, worn_outfits_percentage=worn_outfits_percentage, worn_outfits=worn_outfits_in_season.count(), total_outfits=number_of_days_in_season, is_latest=True, season=season)
            if latest:
                latest.is_latest = False
                latest.save()
            return season
    
    @action(detail=False, methods=['get'])
    def get_stats(self, request):
        print("Request ", request)
        print("Query params ", request.query_params)
        user = request.query_params['userId']
        # get the latest stats for the user and if it is not for the current month, compute the stats
        latest = Stats.objects.filter(wardrobe__user_id=user).filter(is_latest=True).first()
        print("Latest ", latest)
        if not latest or latest.last_calculated.month != date.today().month:
            print("Compute stats")
            self.compute_wardrobe_usage(user)
            latest = Stats.objects.filter(wardrobe__user_id=user).filter(is_latest=True).first()
            
        return Response(data=StatsSerializer(latest).data, status=status.HTTP_200_OK)
            
        
        