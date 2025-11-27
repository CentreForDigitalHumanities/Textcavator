from django.contrib.auth import get_user_model

User = get_user_model()


def test_user_crud(db, user_credentials, admin_credentials):
    admin = User.objects.create(**admin_credentials)
    user = User.objects.create(**user_credentials)

    assert len(User.objects.all()) == 2
    assert admin.username == 'admin'
    assert user.email == 'basicuser@textcavator.com'
    assert admin.profile

    admin.is_superuser = True
    admin.is_staff = True
    admin.save()


    admin.delete()
    user.delete()

    assert len(User.objects.all()) == 0
