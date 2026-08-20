from bow import models
from django.contrib import admin

class AddBOWFieldTaskAdmin(admin.StackedInline):
    model = models.AddBOWFieldTask
    extra = 0

class PopulateBOWFieldTaskAdmin(admin.StackedInline):
    model = models.PopulateBOWFieldTask
    extra = 0
