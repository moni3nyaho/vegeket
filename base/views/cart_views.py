from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.views.generic import View, ListView
from base.models import Item
from collections import OrderedDict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages

class CartListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'pages/cart.html'

    def get_queryset(self):
        cart = self.request.session.get('cart', None)
        if cart is None or len(cart) == 0:
            return redirect('/')
        self.queryset = []
        self.total = 0
        for item_pk, quantity in cart['items'].items():
            obj = Item.objects.get(pk=item_pk)
            obj.quantity = quantity
            obj.subtotal = int(obj.price * quantity)
            self.queryset.append(obj)
            self.total += obj.subtotal
        self.tax_included_total = int(self.total * (settings.TAX_RATE + 1))
        cart['total'] = self.total
        cart['tax_included_total'] = self.tax_included_total
        self.request.session['cart'] = cart
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["total"] = self.total
            context["tax_included_total"] = self.tax_included_total
        except Exception:
            pass
        return context

class AddCartView(LoginRequiredMixin, View):
    def post(self, request):
        item_pk = request.POST.get('item_pk')
        quantity = int(request.POST.get('quantity', 1))
        item = get_object_or_404(Item, pk=item_pk)
        cart = request.session.get('cart', None)
        if cart is None or len(cart) == 0:
            items = OrderedDict()
            cart = {'items' : items}
        existing_qty = cart['items'].get(item_pk, 0)
        new_total = existing_qty + quantity
        if new_total > item.stock:
            allowed = max(item.stock - existing_qty, 0)
            if allowed > 0:
                messages.error(request, f"在庫が足りません　(あと{allowed}個まで追加できます)")
            else:
                messages.error(request, "これ以上カートに追加できません　(在庫なし)")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        # if item_pk in cart['items']:
        #     cart['items'][item_pk] += quantity
        # else:
        #     cart['items'][item_pk] = quantity
        # request.session['cart'] = cart
        # return redirect('/cart/')

        cart['items'][item_pk] = new_total
        request.session['cart'] = cart

        messages.success(request, f"{item.name}をカートに追加しました！")
        return redirect('/cart/')

@login_required
def remove_from_cart(request, pk):
    cart = request.session.get('cart', None)
    if cart is not None:
        del cart['items'][pk]
        request.session['cart'] = cart
    return redirect('/cart/')