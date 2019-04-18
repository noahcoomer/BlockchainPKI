from django.contrib import admin
from .models import Block


# Register your models here.
class BlockAdmin(admin.ModelAdmin):
    list_display = ['header', 'hashValue']

    class Meta:
        model = Block

admin.site.register(Block, BlockAdmin)
from django.contrib import admin
