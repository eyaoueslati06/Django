from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from PIL import Image
from django.forms import ModelForm;
from django import forms;
from django.core.files.base import ContentFile
import requests

# Create your models here.
class Utilisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)
    phonenumber = models.CharField(max_length=20, null=True)
    date_naissance = models.DateField(null=True, default='2001-01-01')
    Address = models.CharField(max_length=256, null=True)
    City = models.CharField(max_length=256, null=True)
    Country = models.CharField(max_length=256, null=True)
    postal_code = models.CharField(max_length=20, null=True)
    about_me = models.TextField(null=True)
    avatar = models.ImageField(default='Tortuga.png', upload_to='profile_images')
    USERNAME_FIELD = 'pseudo'
    subscription_type_choices = (
        ('explorateur', 'Explorateur'),
        ('infopreneur', 'Infopreneur'),
        ('business', 'Business'),
    )
    Abonnement = models.CharField(max_length=20, choices=subscription_type_choices, default='explorateur', null=True)

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
class UtilisateurUpdateForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['Address', 'City', 'Country', 'postal_code', 'about_me', 'avatar', 'phonenumber', 'date_naissance']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['Address', 'City', 'Country', 'postal_code', 'about_me', 'avatar', 'phonenumber', 'date_naissance']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

    # Include User fields
    username = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=30 )
    last_name = forms.CharField(max_length=30 )
    email = forms.EmailField(max_length=254)
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].initial = self.instance.user.username
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name
        self.fields['email'].initial = self.instance.user.email
        self.fields['date_naissance'].required = False
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.user_id).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.user_id).exists():
            raise forms.ValidationError('This email is already taken.')
        return email

    def save(self, commit=True):
        utilisateur = super(UserProfileForm, self).save(commit=False)
        user = self.instance.user

        # Update User fields
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        # Update Utilisateur fields
        utilisateur.Address = self.cleaned_data['Address']
        utilisateur.City = self.cleaned_data['City']
        utilisateur.Country = self.cleaned_data['Country']
        utilisateur.postal_code = self.cleaned_data['postal_code']
        utilisateur.about_me = self.cleaned_data['about_me']
        utilisateur.avatar = self.cleaned_data['avatar']
        utilisateur.phonenumber = self.cleaned_data['phonenumber']
        utilisateur.date_naissance = self.cleaned_data['date_naissance']

        if commit:
            user.save()
            utilisateur.save()
        return utilisateur

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['phonenumber']
        widgets = {}

    # Include User fields
    username = forms.CharField(max_length=30, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    def __init__(self, *args, **kwargs):
        super(AdminProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].initial = self.instance.user.username
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name
        self.fields['email'].initial = self.instance.user.email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError('This email is already taken.')
        return email

    def save(self, commit=True):
        utilisateur = super(AdminProfileForm, self).save(commit=False)
        user = self.instance.user

        # Update User fields
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        # Update Utilisateur fields
        utilisateur.phonenumber = self.cleaned_data['phonenumber']

        if commit:
            user.save()
            utilisateur.save()
        return utilisateur



   
    
         
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Utilisateur.objects.create(user=instance)


class Contactt(models.Model):
    id_c= models.IntegerField(primary_key = True)
    

class Contact(models.Model):
    id_infopreneur =models.ForeignKey(User,on_delete=models.CASCADE,default=0)
    name = models.CharField(max_length=100)  
    email = models.EmailField(null=True)  
    contact = models.CharField(max_length=15)
    categorie= models.CharField(max_length=100, null=True)
    sexe_type = (
        ('femme', 'Femme'),
        ('homme', 'Homme'),
        ('autre', 'Autre'),
    )
    Sexe = models.CharField(max_length=30, choices=sexe_type, default='homme', null=True)
    class Meta:  
        db_table = "Contactt"

   
class Produit(models.Model):
    id= models.IntegerField(primary_key = True)
    id_infopreneur =models.ForeignKey(User,on_delete=models.CASCADE,default='0')
    nom = models.CharField(max_length=25)    
    prix = models.DecimalField(max_digits=6, decimal_places=2)             
    description = models.CharField(max_length=500) 
    CATEGORIE = [
    ('img', 'IMAGE'),
    ('VD', 'VIDEO'),
    ('B', 'Ebook'),
    ('T', 'TICKET'),
    ('pdf', 'Portable Document Format'),
                ]


class Affilie(models.Model):
     nom_prenom=models.CharField(max_length=60,null=True)
     email = models.EmailField(null=True)
     contact = models.CharField(max_length=15,null=True)
     contrat=models.CharField(max_length=256,null=True)
     pourcentage=models.CharField(max_length=15,null=True)
     id_infopreneur =models.ForeignKey(User,on_delete=models.CASCADE,default='0')

class TemplatesCommuns(models.Model):
     id = models.AutoField(primary_key=True)
     title = models.CharField(max_length=30,null=True)
     codeHtml=models.TextField(null=True)
     type=models.CharField(max_length=30,null=True)
     image = models.ImageField(null=True)
     
class TemplatesUser(models.Model):
     id= models.IntegerField(primary_key = True)
     title = models.CharField(max_length=30,null=True)
     codeHtml=models.TextField(null=True)
     type=models.CharField(max_length=30,null=True)
     URL=models.TextField(null=True)
     description=models.TextField(null=True)
     id_infopreneur =models.ForeignKey(User,on_delete=models.CASCADE,default='0')
     id_Commun =models.ForeignKey(TemplatesCommuns,on_delete=models.CASCADE,default='0')
     image = models.ImageField(null=True)

class FormPopUp(models.Model):
    id= models.IntegerField(primary_key = True)
    title = models.CharField(max_length=30,null=True)
    description=models.TextField(null=True)
    codeHtml=models.TextField(null=True)
    image = models.ImageField(null=True)
    URL=models.TextField(null=True)

class ContactFormSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phonenumber = models.CharField(max_length=20,null=True)
    subject = models.CharField(max_length=200,null=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

class ContactGoogle(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    content = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='post_images/')    
    id_infopreneur =models.ForeignKey(User,on_delete=models.CASCADE,default=0)
    categorie_type = (
        ('bien-être corps cœur esprit', 'Bien-être Corps Cœur Esprit'),
        ('développement personnel et spirituel', 'Développement Personnel et Spirituel'),
        ('coaching professionnel et relationnel', 'Coaching Professionnel et Relationnel'),
    )
    Categorie = models.CharField(max_length=80, choices=categorie_type, default='bien-être corps cœur esprit', null=True)
    
class Page(models.Model):
    url = models.URLField()
    html_file = models.FileField(upload_to='html_files', null=True, blank=True)

    def download_html(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            file_name = self.url.split('/')[-1]
            content = ContentFile(response.content)
            self.html_file.save(file_name, content, save=True)

class Commande(models.Model):
    num_commande=models.IntegerField(null=True)
    date_commande=models.DateField(null=True)
    nom_client= models.CharField(max_length=35, null=True)
    prenom_client= models.CharField(max_length=25, null=True)
    ville=models.CharField(max_length=256, null=True)
    montant_commande=models.DecimalField(max_digits=6, decimal_places=2, null=True)
    ugs = models.CharField(max_length=256, null=True) 
    id_produit=models.IntegerField(null=True)
    nom_produit=models.CharField(max_length=256, null=True)
    categorie=models.CharField(max_length=500, null=True)
    prix_produit=models.DecimalField(max_digits=6, decimal_places=2, null=True)
    description_produit=models.CharField(max_length=500)
    id_infopreneur =models.ForeignKey(User,on_delete=models.CASCADE,default=0)
    sexe_type = (
        ('femme', 'Femme'),
        ('homme', 'Homme'),
        ('autre', 'Autre'),
    )
    Sexe = models.CharField(max_length=30, choices=sexe_type, default='homme', null=True)
    

