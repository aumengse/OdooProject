# -*- coding: utf-8 -*-

from openerp import api, fields, models
from datetime import datetime, timedelta
import time

class Reseller(models.Model):
    _name = 'payment_reseller.reseller'
    
    name =fields.Char(string="Fullname", required=True)
    address = fields.Char(string="Address")
    
class Prod(models.Model):
    _name = 'payment_reseller.products'
    
    name=fields.Char(string="Product Name", size= 100)
    rs_price=fields.Float(string="Price")
    
class PO(models.Model):
    _name = "payment_reseller.po"
    
    po_date =fields.Date(string="Date", default = lambda *a: time.strftime('%Y-%m-%d'))
    name = fields.Many2one(string="Reseller")
    prod_name = fields.Many2one(string="Products")
    qty = fields.Integer(string="Quantity")
    discount = fields.Integer(string="Discount(%)")
    price = fields.Float(string="Price")
    
