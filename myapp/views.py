from django.shortcuts import render, redirect  
from myapp.forms import ContactForm  
from myapp.forms import ShareForm 
from myapp.forms import UtilisateurForm
from myapp.models import Contact  
from myapp.forms import UserForm
from myapp.forms import *
from django.contrib.auth import authenticate,login
from django.forms import ValidationError
from django.views.generic import View
from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm ,UsernameField,PasswordChangeForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from myapp.models import Utilisateur
from django.http import JsonResponse
from .models import Utilisateur
from django.shortcuts import render, get_object_or_404
from .forms import UtilisateurUpdateForm
from .forms import TemplatesUpdateForm
from .forms import TemplatesCreateForm
from django.contrib.auth.forms import UserChangeForm
from django.http import Http404
import logging
from .models import ContactGoogle
from .forms import ContactForm
from nbconvert import HTMLExporter
import nbformat
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from django.core.files.base import ContentFile
from django.shortcuts import render
from .models import Page
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import base64
import os
from django.conf import settings
from django.http import HttpResponseServerError
from django.http import HttpResponseBadRequest
from django.db.models import Count
from django.db.models import Sum, Count
import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import F

def notebook_view(request):
    with open('chatbot/ChatbotApp.py') as f:
        code = f.read()
    notebook = nbformat.reads(code, asversion=4)
    exporter = HTMLExporter()
    html,  = exporter.from_notebook_node(notebook)

    return render(request, 'notebook.html', {'html': html})

@csrf_exempt
def save_image(request):
    if request.method == 'POST':
        # Get the image data from the request
        image_data = request.FILES['image'].read()

        # Save the image to a file in the media folder
        media_path = os.path.join(settings.MEDIA_ROOT, 'image.png')
        with open(media_path, 'wb') as f:
            f.write(image_data)

        # Generate the URL of the saved image
        image_url = request.build_absolute_uri(reverse('imagedisplay')) + '?path=image.png'

        # Return the URL of the saved image in a JSON response
        return JsonResponse({'image_url': image_url})

    return HttpResponseBadRequest('Invalid request method')

def imagedisplay(request):
    image_url = None
    try:
        with open(os.path.join(settings.MEDIA_ROOT, 'image.png'), 'rb') as f:
            image_url = request.build_absolute_uri(settings.MEDIA_URL + 'image.png')
    except IOError:
        pass
    return render(request, 'imagedisplay.html', {'image_url': image_url})   
 

class SignupView(View):

    
    def get(self, request):
        return render(request, 'signup.html')
    
    def post(self, request):
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('/signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('/signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken.")
            return redirect('/signup')
        
        user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password1)
        user.save()
        
        messages.success(request, "Signup successful!")
        return redirect('/adminDashboard')


logger = logging.getLogger(__name__)
class MyloginView(View):
    def get(self, request):
        fm = MyLoginForm()  # create an instance of the login form
        return render(request, 'login.html', {'form': fm})  # render the login page with the login form

    def post(self, request):
        fm = MyLoginForm(request, data=request.POST)  # create an instance of the login form with POST data
        if fm.is_valid():  # check if the form data is valid
            username = fm.cleaned_data['username']  # get the username from the form data
            password = fm.cleaned_data['password']  # get the password from the form data
            user = authenticate(request, username=username, password=password)  # authenticate the user
            if user is not None:  # if the user is authenticated
                login(request, user)  # log the user in
                if user.is_superuser:  # Check if user is an admin
                    refresh = RefreshToken.for_user(user)  # generate a JWT refresh token
                    token = str(refresh.access_token)  # get the access token from the refresh token
                    return redirect(reverse_lazy('homeadmin'), token=token)  # redirect to the admin dashboard with the token in the URL
                else:
                    return redirect(reverse_lazy('acceuil'))  # redirect to the home page
        else:
            return render(request, 'login.html', {'form': fm})  # render the login page with the invalid form data



@login_required
def addnew(request):  
    if request.method == "POST":  
        form = ContactForm(request.POST)  
        if form.is_valid():  
            try:
                # Get the ID of the current user
                user_id = request.user.id
                
                # Save the form and set the user ID of the Affilie model
                contact = form.save(commit=False)
                contact.id_infopreneur_id = user_id
                contact.save()
                
                return redirect('/index')  
            except:  
                pass
    else:  
        form = ContactForm()  
    return render(request,'index.html',{'form':form}) 
 
 
@login_required
def index(request):
    # Get the ID of the current user
    user_id = request.user.id
    
    # Filter the Affilie objects by the user ID
    contacts = Contact.objects.filter(id_infopreneur_id=user_id)
    
    return render(request, 'show.html', {'contacts': contacts})
 
def edit(request, id):  
    contact = Contact.objects.get(id=id)  
    return render(request,'edit.html', {'contact':contact})  
 
def update(request, id):
    contact = Contact.objects.get(id=id)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect("/index")
    else:
        form = ContactForm(instance=contact)
        
    context = {
        'form': form,
        'contact': contact
    }

    return render(request, 'edit.html', context)  
     
def destroy(request, id):  
    contact = Contact.objects.get(id=id)  
    contact.delete()  
    return redirect("/index")  
@login_required
def addnewa(request):  
    if request.method == "POST":  
        form = AffilieForm(request.POST)  
        if form.is_valid():  
            try:
                # Get the ID of the current user
                user_id = request.user.id
                
                # Save the form and set the user ID of the Affilie model
                affilie = form.save(commit=False)
                affilie.id_infopreneur_id = user_id
                affilie.save()
                
                return redirect('/indexa')  
            except:  
                pass
    else:  
        form = AffilieForm()  
    return render(request,'indexa.html',{'form':form})

@login_required
def indexa(request):
    # Get the ID of the current user
    user_id = request.user.id
    
    # Filter the Affilie objects by the user ID
    affilies = Affilie.objects.filter(id_infopreneur_id=user_id)
    
    return render(request, 'showaffilie.html', {'affilies': affilies})

 
def edita(request, id):  
    affilie = Affilie.objects.get(id=id)  
    return render(request,'edita.html', {'affilie':affilie})  
 
def updatea(request, id):  
    affilie = Affilie.objects.get(id=id)  
    form = AffilieForm(request.POST, instance = affilie)  
    if form.is_valid():  
        form.save()  
        return redirect("/indexa")  
    return render(request, 'edita.html', {'affilie':affilie}) 

def destroya(request, id):  
    affilie = Affilie.objects.get(id=id)  
    affilie.delete()  
    return redirect("/indexa")  

def home(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        response = requests.post('http://localhost:5000/message', json={'message': message}).json()
        bot_response = response['response']
        return JsonResponse({'bot_response': bot_response})
    else:
        return render(request, 'home.html')




def reclamation(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phonenumber = request.POST['phonenumber']
        subject = request.POST['subject']
        message = request.POST['message']
        submission = ContactFormSubmission(name=name, email=email, phonenumber=phonenumber, subject=subject, message=message)
        submission.save()
        # Return a response

    return render(request, 'reclamation.html')

def destroyadmin(request, id):  
    template = ContactFormSubmission.objects.get(id=id)  
    template.delete()  
    return redirect("/rec_admin") 


def acceuil(request):
    user_id = request.user.id

    contacts = Contact.objects.filter(id_infopreneur_id=user_id)
    tunnels = Post.objects.filter(id_infopreneur_id=user_id)
    affilies = Affilie.objects.filter(id_infopreneur_id=user_id)
    user = request.user

    contact_count = user.contact_set.count()
    affiliate_count = user.affilie_set.count()
    post_count = user.post_set.count()

    contacts_list = list(contacts.values('Sexe'))
    contacts_json = json.dumps(contacts_list)

    commandes = Commande.objects.all()

    data = [
        {
            'date_commande': commande.date_commande.strftime('%Y-%m-%d'),
            'montant_commande': commande.montant_commande
        }
        for commande in commandes
    ]

    top_clients = (
    Commande.objects.filter(id_infopreneur_id=user_id)
    .values('nom_client', 'prenom_client')
    .annotate(count=Count('id'))
    .order_by('-count')[:3]
                )
    


    chiffre_affaires = commandes.aggregate(total_chiffre_affaires=Sum('montant_commande'))['total_chiffre_affaires'] or 0

    male_clients = Commande.objects.filter(id_infopreneur_id=user_id, Sexe='homme')
    female_clients = Commande.objects.filter(id_infopreneur_id=user_id, Sexe='femme')
    other_clients = Commande.objects.filter(id_infopreneur_id=user_id, Sexe='autre')

    male_clients_count = male_clients.count()
    female_clients_count = female_clients.count()
    other_clients_count = other_clients.count()
    def convert_currency(amount, base_currency, target_currency):
        # Make API request to get the latest exchange rates
        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base_currency}")

        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates")
            if rates:
                conversion_rate = rates.get(target_currency)
                if conversion_rate:
                    converted_amount = Decimal(amount) * Decimal(str(conversion_rate))
                    return converted_amount

        return None

    chiffre_affaires_euros = convert_currency(chiffre_affaires, "TND", "EUR")
    chiffre_affaires_dollars = convert_currency(chiffre_affaires, "TND", "USD")



    context = {
        'male_clients': male_clients,
        'female_clients': female_clients,
        'other_clients': other_clients,
        'male_clients_count': male_clients_count,
        'female_clients_count': female_clients_count,
        'other_clients_count': other_clients_count,
        'contact_count': contact_count,
        'affiliate_count': affiliate_count,
        'post_count': post_count,
        'contacts': contacts,
        'affilies': affilies,
        'tunnels': tunnels,
        'contacts_json': contacts_json,
        'commandes': commandes,
        'data': data,
        'top_clients': top_clients,
        'chiffre_affaires': chiffre_affaires,
        'chiffre_affaires_euros': chiffre_affaires_euros,
        'chiffre_affaires_dollars': chiffre_affaires_dollars,
        
    }

    return render(request, 'acceuil.html', context)


def homeadmin(request):
    utilisateurs=Utilisateur.objects.all()
    posts = Post.objects.all()
    chart_data = {}

    for post in posts:
        username = post.id_infopreneur.username
        chart_data[username] = chart_data.get(username, 0) + 1
    reclamation_data = ContactFormSubmission.objects.values('submitted_at').annotate(count=Count('id')).order_by('submitted_at')
    date_counts = {}
    for data in reclamation_data:
        date = data['submitted_at'].strftime('%Y-%m-%d')
        date_counts[date] = date_counts.get(date, 0) + 1

        sorted_dates = sorted(date_counts.keys())
        counts = [date_counts[date] for date in sorted_dates]

   

    context = {
        'chart_data': chart_data,
        'utilisateurs':utilisateurs,
        'sorted_dates': sorted_dates,
        'counts': counts,
    }
    return render(request,'homeadmin.html',context)


def landingpage(request):
    # Get the ID of the current user
    user_id = request.user.id
   
     # Filter the Affilie objects by the user ID
    post= Post.objects.filter(id_infopreneur_id=user_id)
    return render(request,"landingpage.html",{'post':post}) 
def destroypost(request, id):  
    post = Post.objects.get(id=id)  
    post.delete()  
    return redirect("/landingpage")

def preview(request):
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the ID of the current user
            user_id = request.user.id
                
            # Save the form and set the user ID of the Affilie model
            post = form.save(commit=False)
            post.id_infopreneur_id = user_id
            post.save()
           
            last_post_id = Post.objects.latest('id').id
            post = Post.objects.get(id=last_post_id)  
            
            return render(request, 'template1.html', {'post': post})
    else:
        form = PostForm()
    return render(request, 'preview.html', {'form': form})

def template1(request, id):  
    post = Post.objects.get(id=id)      
    return render(request,'template1.html', {'post':post}) 
def preview2(request):
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the ID of the current user
            user_id = request.user.id
                
            # Save the form and set the user ID of the Affilie model
            post = form.save(commit=False)
            post.id_infopreneur_id = user_id
            post.save()
           
            last_post_id = Post.objects.latest('id').id
            post = Post.objects.get(id=last_post_id)  
            
            return render(request, 'template2.html', {'post': post})
    else:
        form = PostForm()
    return render(request, 'preview2.html', {'form': form})

def template2(request, id):  
    post = Post.objects.get(id=id)     
    return render(request,'template2.html', {'post':post}) 



def profile(request, user_id):
    utilisateur = Utilisateur.objects.get(user_id=user_id)
    user = User.objects.get(id=user_id)
    date_joined = user.date_joined

    # Check if date_joined is not None
    if date_joined is not None:
        # Format date_joined to "yyyy-MM-dd HH:mm:ss" format
        date_joined_formatted = date_joined.strftime('%Y-%m-%d %H:%M:%S')

        # Calculate the countdown date as 30 days from the date joined
        countdown_date = date_joined + timedelta(days=30)
    else:
        # Handle the case where date_joined is None
        date_joined_formatted = None
        countdown_date = None

    context = {'utilisateur': utilisateur, 'user_id': user_id, 'date_joined_formatted': date_joined_formatted, 'countdown_date': countdown_date}
    return render(request, 'profile.html', context)

def profiladmin(request, user_id):
    utilisateur = Utilisateur.objects.get(user_id=user_id)
    user = User.objects.get(id=user_id)
    date_joined = user.date_joined

    # Check if date_joined is not None
    if date_joined is not None:
        # Format date_joined to "yyyy-MM-dd HH:mm:ss" format
        date_joined_formatted = date_joined.strftime('%Y-%m-%d %H:%M:%S')

        # Calculate the countdown date as 30 days from the date joined
        countdown_date = date_joined + timedelta(days=30)
    else:
        # Handle the case where date_joined is None
        date_joined_formatted = None
        countdown_date = None

    context = {'utilisateur': utilisateur, 'user_id': user_id, 'date_joined_formatted': date_joined_formatted, 'countdown_date': countdown_date}
    return render(request, 'profiladmin.html', context)



@login_required
def updateprofile1(request, utilisateur_id):
    utilisateur = Utilisateur.objects.get(id=utilisateur_id)
    user = utilisateur.user

    if request.method == 'POST':
        fields = request.POST.dict()
        avatar_file = request.FILES.get('avatar')
        # Store the existing avatar URL
        existing_avatar_url = utilisateur.avatar.url if utilisateur.avatar else None

        # Update other fields
        for field_name, field_value in fields.items():
            if hasattr(utilisateur, field_name):
                if field_name == 'date_naissance':
                    try:
                        date_value = datetime.strptime(field_value, '%Y-%m-%d').date()
                        setattr(utilisateur, field_name, date_value)
                    except ValueError:
                        pass
                else:
                    setattr(utilisateur, field_name, field_value)
            if hasattr(user, field_name):
                setattr(user, field_name, field_value)

        if avatar_file:
            # Read the file content
            file_content = avatar_file.read()
            # Set the file content as the avatar field value
            utilisateur.avatar.save(avatar_file.name, ContentFile(file_content))
        elif existing_avatar_url:
            # Preserve the existing avatar if no new avatar file is provided
            setattr(utilisateur, 'avatar', existing_avatar_url)

        # Save the utilisateur and user objects
        utilisateur.save()
        user.save()

        return redirect('profile', utilisateur_id)

    return render(request, 'updateprofile1.html', {'utilisateur_id': utilisateur_id, 'utilisateur': utilisateur})


@login_required
def updateprofile1admin(request, utilisateur_id):
    utilisateur = Utilisateur.objects.get(id=utilisateur_id)
    user = utilisateur.user

    if request.method == 'POST':
        fields = request.POST.dict()
        avatar_file = request.FILES.get('avatar')
        # Store the existing avatar URL
        existing_avatar_url = utilisateur.avatar.url if utilisateur.avatar else None

        # Update other fields
        for field_name, field_value in fields.items():
            if hasattr(utilisateur, field_name):
                if field_name == 'date_naissance':
                    try:
                        date_value = datetime.strptime(field_value, '%Y-%m-%d').date()
                        setattr(utilisateur, field_name, date_value)
                    except ValueError:
                        pass
                else:
                    setattr(utilisateur, field_name, field_value)
            if hasattr(user, field_name):
                setattr(user, field_name, field_value)

        if avatar_file:
            # Read the file content
            file_content = avatar_file.read()
            # Set the file content as the avatar field value
            utilisateur.avatar.save(avatar_file.name, ContentFile(file_content))
        elif existing_avatar_url:
            # Preserve the existing avatar if no new avatar file is provided
            setattr(utilisateur, 'avatar', existing_avatar_url)

        # Save the utilisateur and user objects
        utilisateur.save()
        user.save()

        return redirect('profiladmin', utilisateur_id)

    return render(request, 'updateprofile1admin.html', {'utilisateur_id': utilisateur_id, 'utilisateur': utilisateur})

 
def formpop(request):
    formpops = FormPopUp.objects.all()  
    return render(request,"formpop.html",{'formpops':formpops}) 


def user_list(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    print("Inside user_list function")

    return render(request, 'adminDashboard.html', context)

def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.utilisateur.delete()
    user.delete()
    return redirect('admin_dashboard')

def update_user(request, user_id):
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    
    if request.method == 'POST':
        user_form = UtilisateurUpdateForm(request.POST, instance=utilisateur.user)
        utilisateur_form = UserUpdateForm(request.POST, instance=utilisateur)
        
        if user_form.is_valid() and utilisateur_form.is_valid():
            utilisateur_form.save()
            user_form.save()
            return redirect('admin_dashboard')
    else:
        user_form = UtilisateurUpdateForm(instance=utilisateur.user)
        utilisateur_form = UserUpdateForm(instance=utilisateur)
        
    return render(request, 'user_update.html', {'user_form': user_form, 'utilisateur_form': utilisateur_form})

#liste des templates admin
def pop_admin(request):
    templates = FormPopUp.objects.all()
    context = {
        'templates': templates
    }
    return render(request, 'pop_admin.html', context)

#liste des recs pour l'admin
def rec_admin(request):
    sort_by = request.GET.get('sort_by', 'submitted_at')  # Get the sorting parameter from the request query parameters, defaulting to 'date_submitted'
    templates = ContactFormSubmission.objects.all().order_by(F(sort_by).desc())  # Sort the objects based on the selected parameter
    context = {
        'templates': templates,
        'sort_by': sort_by  # Pass the selected sort parameter to the template for rendering
    }
    return render(request, 'rec_admin.html', context)

#admin creer nouvelle template
def pop_create(request):
    if request.method == 'POST':
        form = PopCreateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.id = None
            template.save()
            return redirect('pop_admin')
    else:
        form = PopCreateForm()
    return render(request, 'pop_template.html', {'form': form})


#delete template admin
def pop_delete(request, id):
    template = FormPopUp.objects.get(id=id)
    template.delete()
    return redirect('pop_admin')

@login_required
def delete_profile(request):
    if request.method == 'POST':
        request.user.delete()
        logout(request)
        return redirect('home')
    return render(request, 'delete_profile.html')

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'change_password.html'
    success_message = "Mot de passe changé"
    success_url = reverse_lazy('acceuil')

class ChangePasswordViewAdmin(SuccessMessageMixin, PasswordChangeView):
    template_name = 'change_passwordadmin.html'
    success_message = "Mot de passe changé"
    success_url = reverse_lazy('profiladmin')
