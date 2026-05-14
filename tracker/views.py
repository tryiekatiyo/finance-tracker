from django.shortcuts import render, redirect
from .models import Transaction, Budget
from .forms import TransactionForm, BudgetForm
from django.contrib.auth.decorators import login_required
from collections import defaultdict

from django.contrib.auth.models import User
from django.contrib import messages


@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)
    budgets = Budget.objects.filter(user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        budget_form = BudgetForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')

        if budget_form.is_valid():
            budget = budget_form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('dashboard')

    else:
        form = TransactionForm()
        budget_form = BudgetForm()

    total_expenses = sum(
        t.amount for t in transactions
        if t.type == 'expense'
    )

    total_income = sum(
        t.amount for t in transactions
        if t.type == 'income'
    )

    transaction_count = transactions.count()

    budget_total = sum(
        b.amount for b in budgets
    )

    remaining = budget_total - total_expenses

    category_data = defaultdict(float)

    for t in transactions:
        if t.type == 'expense':
            category_data[t.category] += float(t.amount)

    categories = list(category_data.keys())
    amounts = list(category_data.values())

    return render(request, 'dashboard.html', {
        'transactions': transactions,
        'budgets': budgets,
        'form': form,
        'budget_form': budget_form,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'transaction_count': transaction_count,
        'budget_total': budget_total,
        'remaining': remaining,
        'categories': categories,
        'amounts': amounts,
    })


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        user.save()

        messages.success(
            request,
            'Account created successfully'
        )

        return redirect('login')

    return render(request, 'register.html')


@login_required
def edit_transaction(request, id):
    transaction = Transaction.objects.get(
        id=id,
        user=request.user
    )

    if request.method == 'POST':
        form = TransactionForm(
            request.POST,
            instance=transaction
        )

        if form.is_valid():
            form.save()
            return redirect('dashboard')

    else:
        form = TransactionForm(instance=transaction)

    return render(request, 'edit_transaction.html', {
        'form': form
    })


@login_required
def delete_transaction(request, id):
    transaction = Transaction.objects.get(
        id=id,
        user=request.user
    )

    transaction.delete()

    return redirect('dashboard')