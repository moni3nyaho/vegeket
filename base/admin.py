from django.contrib import admin
from django.contrib.auth.models import Group
from base.models import Item, Category, Tag, User, Profile, Order
from django.contrib.auth.admin import UserAdmin
from base.forms import UserCreationForm
from django import forms #追記
import json #追記


class TagInline(admin.TabularInline):
    model = Item.tags.through


class ItemAdmin(admin.ModelAdmin):
    inlines = [TagInline]
    exclude = ['tags']

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password',)}),
        (None, {'fields': ('is_active', 'is_admin',)})
    )

    list_display = ('username', 'email', 'is_active',)
    list_filter =()
    ordering = ()
    filter_horizontal = ()

    add_fieldsets = (
        (None, {'fields': ('username', 'email', 'password',)}),
    )

    add_form = UserCreationForm
    inlines = (ProfileInline,)

class CustomJsonField(forms.JSONField): #追記
    def prepare_value(self, value):
        loaded = json.loads(value)
        return json.dumps(loaded, indent=2, ensure_ascii=False)

class OrderAdminForm(forms.ModelForm): #追記
    items = CustomJsonField()
    shipping = CustomJsonField()

    class Meta:
        model = Order
        fields = "__all__"


class OrderAdmin(admin.ModelAdmin): #追記
    form = OrderAdminForm

admin.site.register(Order, OrderAdmin) # OrderAdminを追記
admin.site.register(Item, ItemAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)

