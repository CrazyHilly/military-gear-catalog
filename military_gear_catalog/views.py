from django.shortcuts import render


def contacts_view(request):
    template_name = "contacts.html"
    return render(request, template_name)


def how_to_order_view(request):
    template_name = "how_to_order.html"
    return render(request, template_name)


def about_us_view(request):
    template_name = "about_us.html"
    return render(request, template_name)
