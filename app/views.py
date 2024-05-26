import base64
import string
from django.contrib.auth.models import User
from app.models import ItemProbability, MarketplaceItems, OutfitItem, Wardrobe, WornOutfits, Stats
from rest_framework import permissions, serializers, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
import clothesFeatureExtraction.clothes_recognition_module as ai_model
from openai import OpenAI
from datetime import date
import json
import numpy as np
from app.utils import get_classification_from_gpt

client = OpenAI()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

class WardrobeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wardrobe
        fields = '__all__'

class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stats
        fields = '__all__'

        
# class ItemProbabilitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ItemProbability
#         fields = '__all__'

class ItemProbabilitySerializer(serializers.ModelSerializer):
    max_probability = serializers.SerializerMethodField()
    max_probability_name = serializers.SerializerMethodField()
    preference_grade = serializers.SerializerMethodField()
    temperatureSliderValue = serializers.DecimalField(max_digits=5, decimal_places=2)
    weatherSliderValue = serializers.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        model = ItemProbability
        fields = ['max_probability', 'max_probability_name', 'preference_grade', 'preference', 'temperatureSliderValue', 'weatherSliderValue']

    def get_preference_grade(self, obj):
        # convert the number from [0, 1] to a grade from 1 to 10
        preference = round(obj.preference * 10, 2)
        preference_str = f"{preference:.2f}".rstrip('0').rstrip('.')
        return f"{preference_str} / 10"

    def get_max_probability(self, obj):
        probabilities = {
            "sunnyHot": obj.sunnyHot,
            "sunnyMild": obj.sunnyMild,
            "sunnyCold": obj.sunnyCold,
            "rainyHot": obj.rainyHot,
            "rainyMild": obj.rainyMild,
            "rainyCold": obj.rainyCold,
            "overcastHot": obj.overcastHot,
            "overcastMild": obj.overcastMild,
            "overcastCold": obj.overcastCold,
            "snowyHot": obj.snowyHot,
            "snowyMild": obj.snowyMild,
            "snowyCold": obj.snowyCold
        }
        return max(probabilities.values())

    def get_max_probability_name(self, obj):
        probabilities = {
            "Sunny & Hot": obj.sunnyHot,
            "Sunny & Mild": obj.sunnyMild,
            "Sunny & Cold": obj.sunnyCold,
            "Rainy & Hot": obj.rainyHot,
            "Rainy & Mild": obj.rainyMild,
            "Rainy & Cold": obj.rainyCold,
            "Overcast & Hot": obj.overcastHot,
            "Overcast & Mild": obj.overcastMild,
            "Overcast & Cold": obj.overcastCold,
            "Snowy & Hot": obj.snowyHot,
            "Snowy & Mild": obj.snowyMild,
            "Snowy & Cold": obj.snowyCold
        }
        max_prob_name = max(probabilities, key=probabilities.get)
        return max_prob_name

class OutfitItemSerializer(serializers.ModelSerializer):
    itemprobability = ItemProbabilitySerializer(read_only=True)
    
    class Meta:
        model = OutfitItem
        fields = '__all__'
        
class WornOutfitsSerializer(serializers.ModelSerializer):
    top = OutfitItemSerializer()
    bottom = OutfitItemSerializer()
    shoes = OutfitItemSerializer()
    body = OutfitItemSerializer()

    class Meta:
        model = WornOutfits
        fields = ['date', 'user', 'top', 'bottom', 'shoes', 'body']

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
        preference = round(request.data['preference'], 6) # preferinta intre 0 si 1
    
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
            snowyCold=snowyCold,
            preference=preference,
            weatherSliderValue=weather,
            temperatureSliderValue=temperature
        )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        wardrobe = Wardrobe.objects.filter(user_id=request.user).first()
        
        if not wardrobe:
            return Response(data=[], status=status.HTTP_200_OK)
        
        queryset = self.queryset.filter(wardrobe_id=wardrobe.id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        item = self.get_queryset().filter(id=kwargs['pk']).first()
        
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        new_data = request.data

        for key in new_data.keys():
            if(new_data[key] != None):
                setattr(item, key, new_data[key])

        item.save()

        return Response(data="{}", status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def classify(self, request):
        # category = ai_model.classify_category_from_b64(request.data['image'])        
        # subcategory = ai_model.classify_subcategory_from_b64(request.data['image'], category)
        # color = ai_model.classify_color_from_b64(request.data['image'])
        # season = ai_model.classify_season_from_b64(request.data['image'])
        # usage = ai_model.classify_usage_from_b64(request.data['image'])

        subcategory_prompts = {
            # Topwear
            "A person wearing a T-shirt": "T-shirt", 
            "A person wearing a polo shirt": 'Polo Shirt',
            "A person wearing a shirt": "Shirt", 
            "A person wearing a sweater": "Sweater",
            "A person wearing a jacket": "Jacket", 
            "A person wearing a hoodie": "Hoodie",
            "A blazer": "Blazer", 
            # Bottomwear
            "A pair of jeans": "Jeans",
            "A pair of track pants": "Track Pants",
            "A pair of shorts": "Shorts", 
            "A skirt": "Skirt", 
            "A pair of leggings": "Leggings",
            "A pair of trousers": "Trousers",
            # Bodywear
            "A dress": "Dress",
            "A bodysuit": "Bodysuit",
            "A jumpsuit": "Jumpsuit",
            # Footwear
            "A pair of sneakers": "Sneakers", 
            "A pair of slippers": "Slippers", 
            "A pair of sandals": "Sandals",
            "A pair of flat shoes": "Flats", 
            "A pair of sports shoes": "Sports Shoes", 
            "A pair of heels": "Heels",
            "A pair of hiking shoes": "Hiking Shoes",
            "A pair of boots": "Boots",
            "A pair of sandals with heels": "Sandal Heels",
            # Accessories
            "A tie": "Tie", 
            "A watch": "Watch", 
            "A belt": "Belt", 
            "A jewelry item": "Jewelry", 
            "A handbag": "Handbag", 
            "A backpack": "Backpack", 
            # Headwear
            "A cap": "Cap",
            "A hat": "Hat",
            "A beanie": "Beanie"
        }

        subcategory = subcategory_prompts[ai_model.use_clip(list(subcategory_prompts.keys()), request.data['image'])]
        
        subcategory_mappings = { 'T-shirt': 'Topwear', 'Polo Shirt': 'Topwear', 'Shirt': 'Topwear', 'Sweater': 'Topwear' , 'Jacket': 'Topwear', 'Hoodie': 'Topwear', 'Blazer': 'Topwear',
                                 'Jeans': 'Bottomwear', 'Track Pants': 'Bottomwear', 'Shorts': 'Bottomwear', 'Skirt': 'Bottomwear', 'Leggings': 'Bottomwear', 'Trousers': 'Bottomwear', 
                                 "Dress": "Bodywear", 'Bodysuit': 'Bodywear', 'Jumpsuit': 'Bodywear',
                                 'Sneakers': 'Footwear', 'Slippers': 'Footwear', 'Sandals': 'Footwear', 'Flats': 'Footwear', 'Sports Shoes': 'Footwear', 'Heels': 'Footwear', 'Hiking Shoes': 'Footwear', 'Boots': 'Footwear', 'Sandal Heels': 'Footwear',
                                 'Tie': 'Accessories', 'Watch': 'Accessories', 'Belt': 'Accessories', 'Jewelry': 'Accessories', 'Handbag': 'Accessories', 'Backpack': 'Accessories', 'Cap': 'Headwear', 'Hat': 'Headwear', 'Beanie': 'Headwear' }
        category = subcategory_mappings[subcategory]

        gpt_answers = get_classification_from_gpt(request.data['image'])

        # color_list = [
        #     'white', 'beige', 'black', 
        #     'light gray', 'gray', 'dark gray', 
        #     'yellow',  'dark yellow',  
        #     'light green', 'green', 'dark green', 
        #     'turquoise',  'orange',
        #     'light blue', 'blue', 'dark blue',  
        #     'light pink', 'pink', 'red',
        #     'dark red', 'brown', 'purple', 'multicolor'
        # ]
        # color_labels = [f'A {col} {subcategory.lower()}' for col in color_list]
        # color = ai_model.use_clip(color_labels, request.data['image'])
        # color = find_substring(color, color_list)
        # print(f"color = {color}")

        # materials_list = ['Cotton', 'Wool', 'Silk', 'Synthetic fibers', 'Leather', 'Linen']
        # material_descriptions = [f'A {subcategory.lower()} made of {mat.lower()}' for mat in materials_list]
        # material = ai_model.use_clip(material_descriptions, request.data['image'])
        # material = find_substring(material, materials_list)

        # patterns_list = ['Striped', 'Checkered', 'Floral', 'Dotted', 'Plain', 'Animal print', 'Camouflage', 'Graphic']
        # pattern = ai_model.use_clip([f'A {pat.lower()} {subcategory.lower()}' for pat in patterns_list], request.data['image'])
        # pattern = find_substring(pattern, patterns_list)

        season_mappings = {
            'A clothing item for wearing during spring and autumn': 'Spring,Autumn', 
            'A clothing item for wearing during spring and summer': 'Spring,Summer', 
            'A clothing item for wearing during autumn and winter': 'Autumn,Winter', 
            'A clothing item for wearing during spring': 'Spring', 
            'A clothing item for wearing during summer': 'Summer', 
            'A clothing item for wearing during autumn': 'Autumn',
            'A clothing item for wearing during winter': 'Winter', 
            'A clothing item well suited to all seasons': 'Spring,Summer,Autumn,Winter'
        }
        season = ai_model.use_clip(list(season_mappings.keys()), request.data['image'])
        season = season_mappings[season]

        # usages_list = ['Casual', 'Ethnic', 'Formal', 'Sports', 'Smart Casual', 'Party']
        # usage = ai_model.use_clip([f'A {us.lower()} {subcategory.lower()}' for us in usages_list], request.data['image'])
        # usage = find_substring(usage, usages_list)

        # json = {"category": category, "subcategory": subcategory, "color": color, "season": season, "occasions": usage, "material": material, "pattern": pattern}
        json = {"category": category, "subcategory": subcategory, "color": gpt_answers['color'], "season": season, "occasions": string.capwords(gpt_answers['occasion']), "material": string.capwords(gpt_answers['material']), "pattern": string.capwords(gpt_answers['pattern'])}
        print(f"json = {json}")
        return Response(data=json, status=status.HTTP_200_OK)
    
    def load_img_base64(self, path):
        with open(path, "rb") as f:
            encoded_image = base64.b64encode(f.read())
        return encoded_image

    def outfits_have_more_than_one_item_in_common(self, outfit1, outfit2):
        common_items = 0
        for item1 in outfit1:
            for item2 in outfit2:
                if item1['id'] == item2['id']:
                    common_items += 1
        return common_items > 1
    
    def check_not_enough_items_in_each_category(self, topwear, bottomwear, footwear, bodywear, one_piece):
        if ((len(topwear) < 1 or len(bottomwear) < 1) and not one_piece) or (len(bodywear) < 1 and one_piece) or len(footwear) < 1:
            categories = []
            if len(topwear) < 1:
                categories.append("Topwear")
            if len(bottomwear) < 1:
                categories.append("Bottomwear")
            if len(footwear) < 1:
                categories.append("Footwear")
            if len(bodywear) < 1:
                categories.append("Bodywear")
            return f"Not enough items in each category ({', '.join(categories)}) to form the recommended outfits."
    
    def get_number_of_outfits_possible(self, topwear, bottomwear, footwear, bodywear, num_outfits, one_piece):
        max_outfits = (
            len(bodywear) * len(footwear) if one_piece
            else min(len(topwear) * len(bottomwear), len(topwear) * len(footwear), len(bottomwear) * len(footwear))
        )
        return min(max_outfits, num_outfits)
    
    @action(detail=False, methods=['get'])
    def get_recommendations(self, request, num_outfits=3):
        user = request.query_params['userId']
        wardrobe = Wardrobe.objects.filter(user_id=user).first()
        topwear = OutfitItem.objects.all().filter(category='topwear').filter(wardrobe_id=wardrobe.id)
        bottomwear = OutfitItem.objects.all().filter(category='bottomwear').filter(wardrobe_id=wardrobe.id)
        footwear = OutfitItem.objects.all().filter(category='footwear').filter(wardrobe_id=wardrobe.id)
        bodywear = OutfitItem.objects.all().filter(category='bodywear').filter(wardrobe_id=wardrobe.id)
        
        weather = request.query_params['weather']
        temperature = request.query_params['temperature']
        one_piece = request.query_params['onePiece'] == 'true'
        print("-" * 49)
        print(f"weather = {weather}")
        print(f"temperature = {temperature}")
        
        err = self.check_not_enough_items_in_each_category(topwear, bottomwear, footwear, bodywear, one_piece)
        if err:
            return {"error": err}
        num_outfits = self.get_number_of_outfits_possible(topwear, bottomwear, footwear, bodywear, num_outfits, one_piece)
        
        def compute_clothing_probabilities():
            clothing_probabilities = {}
            for category_items, category_name in [(topwear, "Topwear"), (bottomwear, "Bottomwear"), (footwear, "Footwear"), (bodywear, "Bodywear")]:
                if len(category_items) > 0:
                    print("-" * 20, category_name, "-" * 20)
                    percentages_weatherTemp_given_cloth = [float(getattr(ItemProbability.objects.filter(outfitItem=item.id).first(), weather + temperature)) for item in category_items]
                    probs_weatherTemp_given_cloth = [p / 100 for p in percentages_weatherTemp_given_cloth]
                    print(f"{category_name} P(weather & temp|clothing item) before normalization ", probs_weatherTemp_given_cloth)
                    probs_weatherTemp_given_cloth = ai_model.normalize_probabilities(probs_weatherTemp_given_cloth)
                    print(f"{category_name} P(weather & temp|clothing item) after normalization ", probs_weatherTemp_given_cloth)
                    
                    clothing_prob = [float(getattr(ItemProbability.objects.filter(outfitItem=item.id).first(), "preference")) for item in category_items]
                    print(f"{category_name} P(clothing item) before normalization ", clothing_prob)
                    clothing_prob = ai_model.normalize_probabilities(clothing_prob)
                    print(f"{category_name} P(clothing item) after normalization ", clothing_prob)
                    print()
                    print("Bayes theorem")
                    print("P(clothing item|weather & temp) = P(weather & temp|clothing item) * P(clothing item) / P(weather & temp)")
                    print()
                    print("Law of total probability")
                    print("P(weather & temp) = sum(P(weather & temp|clothing item) * P(clothing item))")
                    print()
                    print("\tprior\t\tmarginal\tlikelihood")
                    new_probabilities = []
                    for prob in probs_weatherTemp_given_cloth:
                        likelihood = prob # P(weather & temp|clothing item)
                        prior = clothing_prob[probs_weatherTemp_given_cloth.index(prob)] # P(clothing item)
                        marginal = round(sum([round(p * cp, 12) for p, cp in zip(probs_weatherTemp_given_cloth, clothing_prob)]), 12) # P(weather & temp)
                        posterior = round(round(likelihood * prior, 12) / marginal, 12)
                        print(f"\t{prior}\t{marginal}\t{likelihood}")
                        new_probabilities.append(posterior)
                    
                    print(f"{category_name} P(clothing item|weather & temp) before normalization ", new_probabilities)
                    new_probabilities = ai_model.normalize_probabilities(new_probabilities, 12)
                    print(f"{category_name} P(clothing item|weather & temp) after normalization ", new_probabilities)
                    clothing_probabilities[category_name] = new_probabilities
            print("-" * 49)
            return clothing_probabilities

        def generate_outfit(clothing_probabilities):
            outfit = []
            if one_piece:
                wear_categories = [(bodywear, "Bodywear"), (footwear, "Footwear")]
            else: 
                wear_categories = [(topwear, "Topwear"), (bottomwear, "Bottomwear"), (footwear, "Footwear")]
            for (category_items, category_name) in wear_categories:
                random_variable = np.random.choice(len(category_items), p=clothing_probabilities[category_name])
                print(f"Category {category_name}, random variable {random_variable}, total items {len(category_items)}, clothing probabilities {clothing_probabilities[category_name]}")
                selected_item = category_items[random_variable]
                outfit.append({"id": selected_item.id, "image": selected_item.image, "category": selected_item.category})
            return outfit

        clothing_probabilities = compute_clothing_probabilities()
        recommendations = []
        while len(recommendations) < num_outfits:
            new_outfit = generate_outfit(clothing_probabilities)
            if all(not self.outfits_have_more_than_one_item_in_common(new_outfit, existing_outfit) for existing_outfit in recommendations):
                recommendations.append(new_outfit)
        
        # switch the first two outfits to have the first outfit in the middle
        if len(recommendations) == 3:
            recommendations[0], recommendations[1] = recommendations[1], recommendations[0]

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
        wornOutfits = WornOutfits.objects.prefetch_related('top', 'bottom', 'shoes', 'body').filter(user=request.user).filter(date__startswith=request.query_params['yearMonth'])
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
        if len(outfitItems) > 2:
            third = OutfitItem.objects.filter(id=outfitItems[2]['id']).first()
            outfitItems = [first, second, third]
        else:
            outfitItems = [first, second]
        
        top = next((obj for obj in outfitItems if obj.category == "Topwear"), None)
        bottom = next((obj for obj in outfitItems if obj.category == "Bottomwear"), None)
        shoes = next((obj for obj in outfitItems if obj.category == "Footwear"), None)
        body = next((obj for obj in outfitItems if obj.category == "Bodywear"), None)

        WornOutfits.objects.create(date=date, user=request.user, top=top, bottom=bottom, shoes=shoes, body=body)

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
        availableItems = MarketplaceItems.objects.prefetch_related('outfit')
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
        images = []
        if 'bodywear' in request.data: # if the outfit is a one piece clothing item (bodywear + footwear)
            bodywear_image = request.data['bodywear']['image']
            footwear_image = request.data['footwear']['image']
            images = [bodywear_image, footwear_image]
        else:
            topwear_image = request.data['topwear']['image']
            bottomwear_image = request.data['bottomwear']['image']
            footwear_image = request.data['footwear']['image']
            images = [topwear_image, bottomwear_image, footwear_image]
        event = request.data['event']
        
        if not event:
            prompt = (
                "Here are images of the selected outfit. Based on their style, color, material, and overall appearance, can these clothes be "
                "combined and look great? Return in JSON with decision (yes or no) and reason. Keep the reason shorter than 140 tokens"
            )
        else:
            prompt = (
                "Here are images of the selected outfit. Based on their style, color, material, overall appearance and the suitability "
                f"for a {event.lower()} occasion, can these clothes be combined and look great? Return in JSON with decision (yes or no) and reason. "
                "Keep the reason shorter than 140 tokens"
            )
        images_description = [
            {
                "type": "image_url",
                "image_url": {
                    "url": image,
                    "detail": "low"
                },
            } for image in images]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        *images_description
                    ],
                }
            ],
            max_tokens=150,
        )

        response = response.choices[0].message.content
        response = json.loads(response.replace('```json', '').replace('```', ''))
        # make all keys lowercase
        response = {k.lower(): v for k, v in response.items()}
        print("response ", response)
        response['reason'] = ".\n".join([f"• {sentence}" for sentence in response['reason'].split(".")[:-1]])
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
    

    # Top 3 Most Used Colors This Month
    # cele mai putin purtate haine din fiecare categorie
    # cat la suta din haine sunt de vreme rece, medie, calda (util de exemplu ca sa vezi ca nu ai destule haine pt cand o sa fie frig)
    @action(detail=False, methods=['get'])
    def get_new_stats(self, request):
        colors_map = {}
        userId = request.query_params['userId']
        for outfit in WornOutfits.objects.filter(user=userId):
            if not outfit.body:
                for item in [outfit.top, outfit.bottom, outfit.shoes]:
                    if item.color.lower().replace(' ', '-') in colors_map:
                        colors_map[item.color.lower().replace(' ', '-')] += 1
                    else:
                        colors_map[item.color.lower().replace(' ', '-')] = 1
            else:
                for item in [outfit.body, outfit.shoes]:
                    if item.color.lower().replace(' ', '-') in colors_map:
                        colors_map[item.color.lower().replace(' ', '-')] += 1
                    else:
                        colors_map[item.color.lower().replace(' ', '-')] = 1

        colors_map = dict(sorted(colors_map.items(), key=lambda item: item[1], reverse=True)[:3])

        # compute the least worn items for each category
        wardrobe = Wardrobe.objects.filter(user_id=userId).first()
        least_worn_items = {}
        for category in ['Topwear', 'Bottomwear', 'Footwear']:
            outfit_items = OutfitItem.objects.filter(wardrobe=wardrobe, category=category)
            least_worn_item = None
            min_worn = float('inf')
            for item in outfit_items:
                worn = WornOutfits.objects.filter(user=userId).filter(top=item).count() + WornOutfits.objects.filter(user=userId).filter(bottom=item).count() + WornOutfits.objects.filter(user=userId).filter(shoes=item).count()
                if worn < min_worn:
                    min_worn = worn
                    least_worn_item = item
            least_worn_items[category] = least_worn_item

        least_worn_items_serialized = {}
        for category, item in least_worn_items.items():
            serializer = OutfitItemSerializer(item)
            least_worn_items_serialized[category] = serializer.data

        # compute the percentage of clothes for each type of weather
        wardrobe_items = OutfitItem.objects.filter(wardrobe=wardrobe)
        total_items = len(wardrobe_items)
        clothing_season_distribution = []
        
        if total_items == 0:
            return Response(data={ "status": "wardrobe empty"}, status=status.HTTP_200_OK) 

        cold_items = wardrobe_items.filter(seasons__contains='Winter').count()
        mild_items = wardrobe_items.filter(seasons_contains='Spring').count() + wardrobe_items.filter(seasons_contains='Autumn').count()
        hot_items = wardrobe_items.filter(seasons__contains='Summer').count()
        cold_percentage = round((cold_items / total_items) * 100, 2)
        mild_percentage = round((mild_items / total_items) * 100, 2)
        hot_percentage = round((hot_items / total_items) * 100, 2)
        clothing_season_distribution = [{'name': 'Cold', 'percent': cold_percentage, 'color': '#00BFFF'}, {'name': 'Mild', 'percent': mild_percentage, 'color': '#ADFF2F'}, {'name': 'Hot', 'percent': hot_percentage, 'color': '#FF4500'}]

        return Response(data={ "status": "ok" ,"topColors":colors_map, "leastWornItems": least_worn_items_serialized, "clothingSeasonDistribution": clothing_season_distribution}, status=status.HTTP_200_OK)
            
        
        