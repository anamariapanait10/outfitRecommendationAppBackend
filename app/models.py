from django.db import models

class Wardrobe(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=255)

class OutfitItem(models.Model):
    id = models.AutoField(primary_key=True)
    wardrobe = models.ForeignKey(Wardrobe, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    subCategory = models.CharField(max_length=30)
    pattern = models.CharField(max_length=30, blank=True, null=True)
    material = models.CharField(max_length=30, blank=True, null=True)
    seasons = models.CharField(max_length=60, blank=True, null=True)
    occasions = models.CharField(max_length=100, blank=True, null=True)
    image = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.id
    
class ItemProbability(models.Model):
    outfitItem = models.OneToOneField(OutfitItem, on_delete=models.CASCADE, primary_key=True, related_name='itemprobability')
    sunnyHot = models.DecimalField(max_digits=5, decimal_places=2)
    sunnyMild = models.DecimalField(max_digits=5, decimal_places=2)
    sunnyCold = models.DecimalField(max_digits=5, decimal_places=2)
    rainyHot = models.DecimalField(max_digits=5, decimal_places=2)
    rainyMild = models.DecimalField(max_digits=5, decimal_places=2)
    rainyCold = models.DecimalField(max_digits=5, decimal_places=2)
    overcastHot = models.DecimalField(max_digits=5, decimal_places=2)
    overcastMild = models.DecimalField(max_digits=5, decimal_places=2)
    overcastCold = models.DecimalField(max_digits=5, decimal_places=2)
    snowyHot = models.DecimalField(max_digits=5, decimal_places=2)
    snowyMild = models.DecimalField(max_digits=5, decimal_places=2)
    snowyCold = models.DecimalField(max_digits=5, decimal_places=2)
    preference = models.DecimalField(max_digits=10, decimal_places=6)
    weatherSliderValue = models.DecimalField(max_digits=5, decimal_places=2)
    temperatureSliderValue = models.DecimalField(max_digits=5, decimal_places=2)
    
    
class Stats(models.Model):
    wardrobe = models.OneToOneField(Wardrobe, on_delete=models.CASCADE)
    season = models.CharField(max_length=30)
    last_calculated = models.DateTimeField(auto_now=True)
    worn_clothes_percentage = models.FloatField()
    worn_outfits_percentage = models.FloatField()
    worn_outfits = models.IntegerField()
    total_outfits = models.IntegerField()
    is_latest = models.BooleanField(default=False)


class WornOutfits(models.Model):
    date = models.CharField(primary_key=True, max_length=12)
    user = models.CharField(max_length=255)
    top = models.ForeignKey(OutfitItem, on_delete=models.CASCADE, related_name='top')
    bottom = models.ForeignKey(OutfitItem, on_delete=models.CASCADE, related_name='bottom')
    shoes = models.ForeignKey(OutfitItem, on_delete=models.CASCADE, related_name='shoes')


class MarketplaceItems(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=250)
    outfit = models.ForeignKey(OutfitItem, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=30)
    images = models.TextField(null=True, blank=True)
    condition = models.CharField(max_length=30)
    size = models.CharField(max_length=30)
    brand = models.CharField(max_length=30)
    posted_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=14)

    def __str__(self):
        return self.id
