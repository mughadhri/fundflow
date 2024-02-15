from django.shortcuts import render,redirect
from django.views.generic import View
from budget.models import Transaction
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.db.models import Sum
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

# Create your views here.

def signin_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

decs=[signin_required,never_cache]


class TransactionForm(forms.ModelForm):

    # create and update>>>>>Modelform
    class Meta:
        model=Transaction
        exclude=("created_data","user_object")
        widgets={
            "title":forms.TextInput(attrs={"class":"form-control"}),
            "amount":forms.NumberInput(attrs={"class":"form-control"}),
            "type":forms.Select(attrs={"class":"form-control form-select"}),
            "category":forms.Select(attrs={"class":"form-control form-select"})
        }
                                       
class RegisterationForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","email","password"]
        widgets={
            "username":forms.TextInput(attrs={"class":"form-control"}),
            "email":forms.EmailInput(attrs={"class":"form-control"}),
            "password":forms.PasswordInput(attrs={"class":"form-control"})
        }

class LoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))


# class TransactionListView(View):
#     def get(self,request,*args,**kwargs):
#         qs=Transaction.objects.filter(user_object=request.user)
#         cur_month=timezone.now().month
#         cur_year=timezone.now().year
#         expense_total=Transaction.objects.filter(
#             user_object=request.user,
#             type="expense",
#             created_date__month=cur_month,
#             created_date__year=cur_year
#         ).aggregate(Sum("amount"))
#         print(expense_total)
#         income_total=Transaction.objects.filter(
#             user_object=request.user,
#             type="income",
#             created_date__month=cur_month,
#             created_date__year=cur_year
#         ).aggregate(Sum("amount"))
#         print(income_total)
#         return render(request,"transaction_list.html",{"data":qs})


@method_decorator(decs,name="dispatch")
class TransactionCreateView(View):
    def get(self,request,*args,**kwargs):
        form=TransactionForm()
        return render(request,"transaction_add.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=TransactionForm(request.POST)

        if form.is_valid():
            data=form.cleaned_data
            Transaction.objects.create(**data,user_object=request.user)
            return redirect("transaction-list")
        else:
            return render(request,"transaction_add.html",{"form":form})

@method_decorator(decs,name="dispatch")
class TransactionDetailView(View):
    def get(self,request,*args,**kwargs):
        # if  not request.user.is_authenticated:
        #     return redirect("signin")
        id=kwargs.get("pk")
        qs=Transaction.objects.get(id=id)

        return render(request,"transaction_detail.html",{"data":qs})
    
    
    # transaction delete
    # localhost:8000/transaction/{id}/remove
    # method:get

@method_decorator(decs,name="dispatch")
class TransactionDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transaction.objects.get(id=id).delete()
        return redirect("transaction-list")
    
@method_decorator(decs,name="dispatch")
class TransactionUpdateView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_object=Transaction.objects.get(id=id)
        form=TransactionForm(instance=transaction_object)
        return render(request,"transaction_edit.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_object=Transaction.objects.get(id=id)
        data=(request.POST)
        form=TransactionForm(data,instance=transaction_object)
        if form.is_valid():
            form.save()
            return redirect("transaction-list")
        else:
            return render(request,"transaction_edit.html",{"form":form})


# signup...............method:get.post.............localhost:8000/signup/
        
class SignUpView(View):
    def get(self,request,*args,**kwargs):
        form=RegisterationForm()
        return render(request,"registration.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=RegisterationForm(request.POST)
        if form.is_valid():
            # form.save().............password ne encrypt chean ahnun commented akiyathu
            User.objects.create_user(**form.cleaned_data)
            print("created")
            return redirect("signin")
        else:
            print("failed ")
            return render(request,"registration.html",{"form":form})



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
    

@method_decorator(decs,name="dispatch")
class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")

@method_decorator(decs,name="dispatch")
class TransactionListView(View):
    def get(self,request,*args,**kwargs):
        qs=Transaction.objects.filter(user_object=request.user)
        
        cur_month=timezone.now().month
        cur_year=timezone.now().year
        print(cur_month,cur_year)
        # expence_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="expense",
        #     created_date__month=cur_month,
        #     created_date__year=cur_year
        # ).aggregate(Sum("amount"))
        # print(expence_total)
        # income_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="income",
        #     created_date__month=cur_month,
        #     created_date__year=cur_year
        # ).aggregate(Sum("amount"))
        # print(income_total)
        data=Transaction.objects.filter(
            created_date__month=cur_month,
            created_date__year=cur_year,
            user_object=request.user,
        ).values("type").annotate(type_sum=Sum("amount"))
        print(data)
        cat_qs=Transaction.objects.filter(
            created_date__month=cur_month,
            created_date__year=cur_year,
            user_object=request.user,
          ).values("category").annotate(cat_sum=Sum("amount"))
        print(cat_qs)
        return render(request,"transaction_list.html",{"data":qs,"type_total":data,"cat_data":cat_qs})
        # .aggregate(Sum("amount"))
        # print(expense_total)
        # income_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="income",
        #     created_date__month=cur_month,
        #     created_date__year=cur_year
        # ).aggregate(Sum("amount"))
        # print(income_total)
        # return render(request,"transaction_list.html",{"data":qs})
    

 
            

