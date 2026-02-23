from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Kullanıcı kayıt işlemleri için serializer.
    Password ve Password2 alanlarını alır, doğrular ve kullanıcıyı oluşturur.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
    
    def validate(self, attrs):
        # Şifrelerin eşleşip eşleşmediğini kontrol et
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Parolalar eşleşmiyor."})
        return attrs

    def create(self, validated_data):
        # Password2 veritabanına kaydedilmez, onu listeden çıkarıyoruz
        validated_data.pop('password2') 
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        
        # Şifreyi hashleyerek kaydet
        user.set_password(validated_data['password'])
        user.save()
        
        return user

class UserSerializer(serializers.ModelSerializer):
    """
    Kullanıcı detaylarını (profil, yetki durumu) dönmek için kullanılır.
    /api/accounts/me/ endpoint'inde çalışır.
    """
    class Meta:
        model = User
        # Frontend'in 'Admin mi?' kontrolü yapabilmesi için 'is_staff' ve 'is_superuser' şart.
        fields = ('id', 'username', 'email', 'is_staff', 'is_superuser')