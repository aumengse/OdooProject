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
    
    name=fields.Char(string="Product Name", size= 50)
    unit = fields.Char(string="Unit", size=10)
    rs_price=fields.Float(string="Price")
    
    
class PO_Head(models.Model):
    _name = "payment_reseller.po_head"
    
    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
                    context={}, count=False, access_rights_uid=None):
    
            if context:
                print 'context', context
                if 'unpaid_po' in context:
                    if context['unpaid_po']:
                        res_payment = self.pool.get('payment_reseller.payment').search(cr, uid,[('invoice_id','!=', False)])
                        inv_ids = []
                        print 'res_payment', res_payment
                        for rec_payment in res_payment:
                            get_pohead = self.pool.get('payment_reseller.po_head').browse(cr, uid, rec_payment)
                            inv_ids.append(get_pohead.invoice_num.id)
                         
                        args.append(("id","in",inv_ids))
            
            return super(PO_Head, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
                                            context=context, count=count, access_rights_uid=access_rights_uid)
    
    name = fields.Char(string="Name", related = "invoice_num")
    po_date =fields.Date(string="Date", default = lambda *a: time.strftime('%Y-%m-%d'))
    invoice_num =fields.Char(string="Invoice",readonly=True)
    reseller_id = fields.Many2one('payment_reseller.reseller',string="Reseller")
    prod_name = fields.One2many('payment_reseller.po_det','po_head_id',string="Products")
    
    @api.model
    def create(self, vals):
        vals['invoice_num'] = self.env['ir.sequence'].get('inv_num')
        
        return super(PO_Head, self).create(vals)
    
class PO_Det(models.Model):
    _name = "payment_reseller.po_det"
   
    prod_id = fields.Many2one('payment_reseller.products',string="Product",required=True)
    po_head_id = fields.Many2one('payment_reseller.po_head', string ="PO Head", ondelete="cascade")
    qty = fields.Float(string="Quantity")
    discount = fields.Float(string="Discount(%)")
    price = fields.Float(string="Price", readonly=True)
    total = fields.Float(string="Total", compute ='_get_total')

    @api.onchange('qty','discount')  
    def _get_total(self):
        for r in self:
            r.total= (r.qty * r.price) - ((r.qty * r.price) * (r.discount/100))
     
    @api.onchange('prod_id')
    def _get_price(self):
        item = self.prod_id
        
        print 'item',item
        
        get_item_price = self.env['payment_reseller.products'].browse(item.id)
        self.price =   get_item_price.rs_price
        
        
    @api.model
    def create(self, vals):
        prod_id = vals['prod_id']
        print 'createitem', prod_id
        get_item_price = self.env['payment_reseller.products'].browse(prod_id)
        vals['price'] = get_item_price.rs_price
        
        return super(PO_Det, self).create(vals)
        
class payment(models.Model):
    _name="payment_reseller.payment"
             
    name = fields.Char(string ="Name", related ="or_num")
    payment_date = fields.Date(string="Date", default = lambda *a: time.strftime('%Y-%m-%d'))
    or_num =fields.Char(string="Receipt", readonly=True)
    rs_id = fields.Many2one('payment_reseller.reseller', string='Reseller')
    invoice_id = fields.Many2one('payment_reseller.po_head', string="Invoice")
    prods = fields.One2many(related="invoice_id.prod_name", readonly = True)
    amt_render = fields.Float(string="Amount Render")
    overpaid = fields.Float(string="Over Payment" ,readonly=True, compute='_compute_amt')
    underpaid = fields.Float(string="Under Payment" ,readonly=True, compute='_compute_amt')
    
    @api.model
    def create(self, vals):
        vals['or_num'] = self.env['ir.sequence'].get('or_code')
        
        return super(payment, self).create(vals)
    
    @api.onchange('rs_id')
    def _onchange_reseller(self):
        selected_reseller = self.rs_id.id
        inv_list = self.env['payment_reseller.po_head'].search([('reseller_id','=',selected_reseller)])
    
        inv_lists= []
        
        for r in inv_list:
            inv_lists.append(r.id)
        return {'domain':{'invoice_id':[('id','in',inv_lists)]},}
    
    @api.depends('amt_render')
    def _compute_amt(self):
        selected_invoice =  self.invoice_id
        print 'selected_invoice', selected_invoice.id
        
        inv_list = self.env['payment_reseller.po_det'].search([('po_head_id','=',selected_invoice.id)])
        print 'inv_list', inv_list
        
        qty_price = 0.00
        total_pur = 0.00
        for r in inv_list:
            print 'qty',r.qty
            print 'price', r.price
            
            qty_price = (r.qty * r.price) - ((r.qty * r.price) * (r.discount/100))
            total_pur = total_pur + qty_price
            qty_price = 0.00
        print 'total_pur', total_pur
        
        payment = self.amt_render - total_pur
        
        print 'payment', payment
        
        if payment > 0:
            self.overpaid = payment
        else:
            self.underpaid = payment