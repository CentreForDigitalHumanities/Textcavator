from bow import models
from django.contrib import admin

class CreateBOWIndexTaskAdmin(admin.StackedInline):
    model = models.CreateBOWIndexTask
    extra = 0

class PopulateBOWIndexTaskAdmin(admin.StackedInline):
    model = models.PopulateBOWIndexTask
    extra = 0
