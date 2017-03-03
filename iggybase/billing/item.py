class Item:
    def __init__ (self, item):
        self.LineItem = item.LineItem
        self.charges = {}
        self.User = item.User
        self.Order = item.Order
        self.PriceItem = item.PriceItem
        self.Organization = item.Organization
        self.OrganizationType = item.OrganizationType
        self.add_charge(item)
        self.ServiceType = item.ServiceType
        self.Invoice = getattr(item, 'Invoice', None)
        self.Institution = getattr(item, 'Institution', None)
        self.amount = (float(self.LineItem.price_per_unit or 0) * int(self.LineItem.quantity or 1))
        self.display_amount = "${:.2f}".format(self.amount)
        # assume no split charges between types
        self.charge_type = item.ChargeMethodType.name

    def add_charge(self, item):
        if item.ChargeMethod.code not in self.charges:
            self.charges[item.ChargeMethod.code] = item

