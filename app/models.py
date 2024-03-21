from django.db import models

class Wardrobe(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=255)

class OutfitItem(models.Model):
    id = models.AutoField(primary_key=True)
    wardrobe_id = models.ForeignKey(Wardrobe, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    pattern = models.CharField(max_length=30, blank=True, null=True)
    material = models.CharField(max_length=30, blank=True, null=True)
    season = models.CharField(max_length=30, blank=True, null=True)
    image = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    


# class Stats(models.Model):
#     wardrobe = models.OneToOneField(Wardrobe, on_delete=models.CASCADE)
#     worn_clothes_percentage = models.FloatField()
#     worn_outfits_percentage = models.FloatField()