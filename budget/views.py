from django.shortcuts import render,redirect
from django.views.generic import View 
from budget.models import Transaction

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.views.decorators.cache import never_cache

class TrasactionForm(forms.ModelForm):

    class Meta:
        model=Transaction
        exclude=("created_date","user_object")
        # fields="__all__"
        # fields=("field1","field2")
    
    # registration form
        
class RegistrationForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","email","password"]

class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField()



# Create your views here.
# view for listing all transactions
# url:localhost/8000/transaction/all

class TransactionListView(View):
    def get(self,request,*args,**kwargs):
        qs=Transaction.objects.filter(user_object=request.user)
        # print(qs.query) : for getting the corresponding mysql qs type query set
        cur_month=timezone.now().month
        cur_year=timezone.now().year
        # print(cur_month,cur_year)

        # expense_tot=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="expense",
        #     created_date__month=cur_month,
        #     created_date__year=cur_year
        # ).aggregate(Sum("amount"))
        # print(expense_tot)
        # income_tot=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="income",
        #     created_date__month=cur_month,
        #     created_date__year=cur_year
        # ).aggregate(Sum("amount"))
        # print(income_tot)

        data=Transaction.objects.filter(
            created_date__month=cur_month,
            created_date__year=cur_year,
            user_object=request.user
        ).values("type").annotate(type_sum=Sum("amount"))
        print(data)

        cat_data=Transaction.objects.filter(
            created_date__month=cur_month,
            created_date__year=cur_year,
            user_object=request.user
        ).values("category").annotate(cat_sum=Sum("amount"))
        print(cat_data)
        
        return render(request,"transaction_list.html",{"data":qs,"type_total":data,"category_total":cat_data})
class TransactionCreateView(View):
    def get(self,request,*args,**kwargs):
        form=TrasactionForm()
        return render(request,"transaction_add.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=TrasactionForm(request.POST)
        if form.is_valid():
            # form.save()
            data=form.cleaned_data
            Transaction.objects.create(**data,user_object=request.user)
            messages.success(request,"Transaction has been added sucessfully")
            return redirect("transaction-list")
        else:
            messages.error(request,"failed to add transaction")
            return render(request,"transaction_add.html",{"form":form})
        
# url:localhost:8000/transactions/{id}/
# method:get

class TransactionDetailView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Transaction.objects.get(id=id)
        return render(request,"transaction_detail.html",{"data":qs})


class TransactionDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transaction.objects.filter(id=id).delete()
        messages.success(request,"Transaction has been deleted successfully")
        return redirect("transaction-list")
# transactionupdateview
# url=localhost:8000/transactions/{id}/change/
# method:get,post
    
class transactionupdateView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_objects=Transaction.objects.get(id=id)
        form=TrasactionForm(instance=transaction_objects)
        return render(request,"transaction_edit.html",{"form":form})
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_objects=Transaction.objects.get(id=id)
        form=TrasactionForm(request.POST,instance=transaction_objects)
        if form.is_valid():
            form.save()
            messages.success(request,"transaction has been updated successfully")
            return redirect("transaction-list")
        else:
            messages.error(request,"failed to update transaction")
            return render(request,"transaction_edit.html",{"form":form})
#   signup
# url:localhost:8000/signup/
# method:get,post

class SignUpView(View):
    def get(self,request,*args,**kwargs):
        form=RegistrationForm()
        return render(request,"register.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(**form.cleaned_data)
            print("created")
            return redirect("signin")
        else:
            print("failed")
            return render(request,"register.html",{"form":form})
# signin
# url: localhost:8000/signin/
# method: get,post
class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm() 
        return render(request,"signin.html",{"form":form})

    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")        
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=u_name,password=pwd)
            if user_object:
                login(request,user_object)
                return redirect("transaction-list") 
        return render(request,"signin.html",{"form":form})
class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")

