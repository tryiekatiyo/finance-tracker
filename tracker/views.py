from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()

    return render(request, 'dashboard.html', {
        'transactions': transactions,
        'form': form
    })