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
    test = fields.Char(string="test")
    
class PO_Head(models.Model):
    _name = "payment_reseller.po_head"
    
    po_date =fields.Date(string="Date", default = lambda *a: time.strftime('%Y-%m-%d'))
    name = fields.Many2one('payment_reseller.reseller',string="Reseller")
    prod_name = fields.One2many('payment_reseller.po_det','po_head_id',string="Products")
    
class PO_Det(models.Model):
    _name = "payment_reseller.po_det"
   
    prod_id = fields.Many2one('payment_reseller.products',string="Product",required=True)
    po_head_id = fields.Many2one('payment_reseller.po_head', string ="PO Head")
    qty = fields.Float(string="Quantity")
    discount = fields.Float(string="Discount(%)")
    price = fields.Float(string="Price", related="prod_id.rs_price",readonly=True)
    total = fields.Float(string="Total", compute ='_get_total')

    @api.onchange('qty','discount')  
    def _get_total(self):
        for r in self:
            r.total= (r.qty * r.price) - ((r.qty * r.price) * (r.discount/100))
     
    
class payment_head(models.Model):
    _name="payment_reseller.payment_head"
          
    name = fields.Char(string ="Name", related='reseller_po_id.name')
    payment_date = fields.Date(string="Date",default = lambda *a: time.strftime('%Y-%m-%d'))
    reseller_po_id = fields.Many2one('payment_reseller.po_head.name', string="Payment", required =True)
    prod_paymentdet_id =fields.One2many('payment_reseller.payment_det','po_det_id',string="Products") 
         
class payment_det(models.Model):
    _name ="payment_reseller.payment_det"
         
    payment_head_id = fields.Many2one('payment_reseller.payment_head')     
    po_det_id = fields.Many2one('payment_reseller.po_det',string="Products")