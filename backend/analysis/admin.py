from analysis import models
from django.contrib import admin

class CreateTokenIndexAdmin(admin.StackedInline):
    model = models.CreateTokenIndexTask
    extra = 0

class PopulateTokenIndexAdmin(admin.StackedInline):
    model = models.PopulateTokenIndexTask
    extra = 0
