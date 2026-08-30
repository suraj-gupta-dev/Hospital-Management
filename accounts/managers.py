from django.contrib.auth.models import BaseUserManager



class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password, **extra_kwargs):
        if not email:
            raise ValueError("Email field is required")
        
        email = self.normalize_email(email)

        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_kwargs)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, first_name, last_name, password, **extra_kwargs):
            extra_kwargs.update({
                "is_staff": True,
                "is_varified": True,
                "is_superuser": True
            })
    
            if extra_kwargs.get("is_staff") is not True:
                raise ValueError("Superuser must have is_staff=True.")
            if extra_kwargs.get("is_superuser") is not True:
                raise ValueError("Superuser must have is_superuser=True.")
            
            user = self.create_user(email, first_name, last_name, password, **extra_kwargs)
            return user