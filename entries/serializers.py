from .models import Entry
from rest_framework import serializers

class FullEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = '__all__'

class CreateEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('title', 'description', 'created_by', 'updated_by')

class DisplayEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        exclude = ('slug', 'date_created', 'date_updated')