class Item:
    def __init__ (self, item):
        self.LineItem = item.LineItem
        self.User = item.User
        self.Order = item.Order
        self.PriceItem = item.PriceItem
        self.amount = (int(self.LineItem.price_per_unit or 0) * int(self.LineItem.quantity or 1))
        self.display_amount = "${:.2f}".format(self.amount)

