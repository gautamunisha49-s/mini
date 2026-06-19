from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def home_view(request):
    # अहिले डेटाबेस खाली भएको हुनाले खाली एरे पठाइएको छ
    context = {
        'posts': [], 
        'recent_stories': []
    }
    return render(request, 'home.html', context)

def login_view(request):
    # यदि युजर पहिले नै लगइन छ भने सिधै होमपेजमा पठाइदिने
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        user_in = request.POST.get('username')
        pass_in = request.POST.get('password')
        
        user = authenticate(request, username=user_in, password=pass_in)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
            
    return render(request, 'login.html')

def register_view(request):
    # यदि युजर पहिले नै लगइन छ भने रजिस्टर पेज खोल्न नदिने
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        user_in = request.POST.get('username')
        email_in = request.POST.get('email')
        pass_in = request.POST.get('password')
        
        # युजरनेम पहिले नै कसैले लिइसकेको छ कि छैन चेक गर्ने
        if User.objects.filter(username=user_in).exists():
            return render(request, 'register.html', {'error': 'Username is already taken'})
            
        # नयाँ युजर बनाउने (तर सिधै लगइन गराउने कोड यहाँबाट हटाइएको छ)
        User.objects.create_user(username=user_in, email=email_in, password=pass_in)
        
        # साइनअप सफल भएपछि सिधै लगइन पेजमा रिडाइरेक्ट गर्ने
        return redirect('login')
        
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')