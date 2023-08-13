from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Dish, Order
from .models import User
from decimal import Decimal


def main_page(request):
    dishes = Dish.objects.all()  
    context = {'dishes': dishes}
    return render(request, 'home_page.html', context)

def display_menu(request):
    dishes = Dish.objects.all()
    return render(request, 'menu.html', {'dishes': dishes})

def user_registration(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            return render(request, 'registration.html', {'message': 'Email already registered. Please login or use a different email.'})
        else:
            name = request.POST['name']
            password = request.POST['password']
            User.objects.create(email=email, name=name, password=password)
            return render(request, 'registration.html', {'message': 'Registration successful. You can now log in with your credentials.'})
    return render(request, 'registration.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email, password=password)
            request.session['user_email'] = user.email
            return redirect('user_section')
        except User.DoesNotExist:
            return render(request, 'login.html', {'message': 'Invalid credentials. Access denied.'})
    return render(request, 'login.html')
def take_order(request):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('user_login')

    dishes = Dish.objects.filter(available=True, quantity__gt=0)

    if request.method == 'POST':
        customer_name = request.POST['customer_name']
        order_items = request.POST.getlist('order_items')
        quantities = request.POST.getlist('quantities')
        order_status = "processing"
        total_price = Decimal('0.0')  # Initialize total_price as a Decimal

        # Create the order
        order = Order.objects.create(customer_name=customer_name, status=order_status)

        for dish_id, quantity in zip(order_items, quantities):
            try:
                dish = Dish.objects.get(pk=dish_id)
                quantity = int(quantity)
                if dish.available and dish.quantity >= quantity:
                    # Add the dish to the order and update quantity
                    order.dishes.add(dish)
                    dish.quantity -= quantity
                    dish.save()
                    total_price += dish.price * Decimal(quantity)  # Convert dish.price to Decimal before multiplying
                else:
                    return render(request, 'take_order.html', {'message': f"{dish.name} is not available or out of stock. Order cannot be processed."})
            except Dish.DoesNotExist:
                return render(request, 'take_order.html', {'message': f"Dish with ID {dish_id} not found in the menu."})

        order.total_price = total_price
        order.save()

        return render(request, 'take_order.html', {'message': f"Order added! Order ID: {order.id}"})

    return render(request, 'take_order.html', {'dishes': dishes})




def update_order_status(request):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('user_login')

    if request.method == 'POST':
        order_id = int(request.POST['order_id'])
        new_status = request.POST['new_status']
        try:
            order = Order.objects.get(pk=order_id)
            order.status = new_status
            order.save()
            return render(request, 'update_order_status.html', {'message': 'Order status updated successfully!'})
        except Order.DoesNotExist:
            return render(request, 'update_order_status.html', {'message': f"Order with ID {order_id} not found."})
    return render(request, 'update_order_status.html')


def add_dish(request):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_section')

    if request.method == 'POST':
        dish_id = request.POST['dish_id']
        dish_name = request.POST['dish_name']
        price = float(request.POST['price'])
        available = request.POST['available'] == "yes"
        quantity = int(request.POST['quantity'])

        Dish.objects.create(id=dish_id, name=dish_name, price=price, available=available, quantity=quantity)

        return render(request, 'add_dish.html', {'message': f"{dish_name} added to the menu!"})

    return render(request, 'add_dish.html')

def update_dish_availability(request):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_section')

    if request.method == 'POST':
        dish_id = request.POST['dish_id']
        try:
            dish = Dish.objects.get(pk=dish_id)
            dish.available = request.POST['available'] == "yes"
            dish.quantity = int(request.POST['quantity'])
            dish.save()
            return render(request, 'update_dish_availability.html', {'message': 'Dish availability and quantity updated successfully!'})
        except Dish.DoesNotExist:
            return render(request, 'update_dish_availability.html', {'message': f"Dish with ID {dish_id} not found."})
    return render(request, 'update_dish_availability.html')

def admin_menu(request):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_section')
    return render(request, 'admin_menu.html')


def review_orders(request):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')

    orders = Order.objects.all()

    return render(request, 'review_orders.html', {'orders': orders})

def admin_logout(request):
    if 'admin_logged_in' in request.session:
        del request.session['admin_logged_in']
    return redirect('admin_section')

def user_logout(request):
    if 'user_email' in request.session:
        del request.session['user_email']
    return redirect('main_page')
def admin_section(request):
    # Implement your admin section logic here
    admin_username = "faiyaz"  # Replace with your admin username
    admin_password = "masai"  # Replace with your admin password

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username == admin_username and password == admin_password:
            request.session['admin_logged_in'] = True
            return redirect('admin_menu')
        else:
            return render(request, 'admin_login.html', {'message': 'Invalid credentials. Access denied.'})
    return render(request, 'admin_login.html')
def user_section(request):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('user_login')
    return render(request, 'user_section.html', {'user_email': user_email})
def remove_dish(request):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_section')

    if request.method == 'POST':
        dish_id = request.POST['dish_id']
        try:
            dish = Dish.objects.get(pk=dish_id)
            dish_name = dish.name
            dish.delete()
            return render(request, 'remove_dish.html', {'message': f"{dish_name} removed from the menu!"})
        except Dish.DoesNotExist:
            return render(request, 'remove_dish.html', {'message': f"Dish with ID {dish_id} not found."})

    return render(request, 'remove_dish.html')
def delete_order(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        order.delete()
        return redirect('review_orders')
    except Order.DoesNotExist:
        return redirect('review_orders')