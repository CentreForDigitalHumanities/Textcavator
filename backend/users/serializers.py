from dj_rest_auth.serializers import UserDetailsSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.db import transaction
from users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    can_edit_corpora = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['enable_search_history', 'can_edit_corpora']



class CustomUserDetailsSerializer(UserDetailsSerializer):
    is_admin = serializers.BooleanField(source='is_staff', read_only=True)
    saml = serializers.BooleanField(read_only=True)
    download_limit = serializers.IntegerField(read_only=True)
    profile = UserProfileSerializer()
    name = serializers.CharField(source='get_short_name', read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        fields = ('id', 'name', 'username', 'email', 'saml',
                  'download_limit', 'is_admin', 'profile')


    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)

        if profile_data:
            profile_serializer = UserProfileSerializer()
            profile_serializer.update(instance.profile, profile_data)

        return super().update(instance, validated_data)

class CustomRegistrationSerializer(RegisterSerializer):
    saml = serializers.BooleanField(default=False)

    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.saml = self.data.get('saml', False)
        user.save()
        return user
