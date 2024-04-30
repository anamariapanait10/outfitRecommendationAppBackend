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
    outfitItem = models.ForeignKey(OutfitItem, on_delete=models.CASCADE, primary_key=True)
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
    
    
# class Stats(models.Model):
#     wardrobe = models.OneToOneField(Wardrobe, on_delete=models.CASCADE)
#     worn_clothes_percentage = models.FloatField()
#     worn_outfits_percentage = models.FloatField()
    
class WornOutfits(models.Model):
    date = models.CharField(primary_key=True, max_length=12)
    user_id = models.CharField(max_length=255)
    top = models.ForeignKey(OutfitItem, on_delete=models.CASCADE, related_name='top')
    bottom = models.ForeignKey(OutfitItem, on_delete=models.CASCADE, related_name='bottom')
    shoes = models.ForeignKey(OutfitItem, on_delete=models.CASCADE, related_name='shoes')


class MarketplaceItems(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=255)
    outfit = models.ForeignKey(OutfitItem, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    images = models.TextField(blank=True, null=True)
    condition = models.CharField(max_length=30, null=True, blank=True)
    size = models.CharField(max_length=30, null=True, blank=True)
    brand = models.CharField(max_length=30, null=True, blank=True)
    posted_date = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=30, null=True, blank=True)
    
    def __str__(self):
        return self.id
