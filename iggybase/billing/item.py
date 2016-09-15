class Item:
    def __init__ (self, item):
        self.LineItem = item.LineItem
        self.User = item.User
        self.Order = item.Order
        self.PriceItem = item.PriceItem
        self.Organization = item.Organization
        self.OrganizationType = item.OrganizationType
        self.OrderChargeMethod = item.OrderChargeMethod
        self.ChargeMethod = item.ChargeMethod
        self.ChargeMethodType = item.ChargeMethodType
        self.ServiceType = item.ServiceType
        self.Invoice = getattr(item, 'Invoice', None)
        self.Institution = getattr(item, 'Institution', None)
        self.amount = (float(self.LineItem.price_per_unit or 0) * int(self.LineItem.quantity or 1))
        self.display_amount = "${:.2f}".format(self.amount)

