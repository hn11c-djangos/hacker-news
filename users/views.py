# views.py
from django.shortcuts import render, redirect
from .forms import CreateAccountForm

def create_account(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            # Procesar los datos del formulario y crear la cuenta
            return redirect('login')
    else:
        form = CreateAccountForm()
    return render(request, 'create_account.html', {'form': form})