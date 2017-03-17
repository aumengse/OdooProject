# -*- coding: utf-8 -*-

from openerp import api, fields, models
from datetime import datetime, timedelta
import time

class Reseller(models.Model):
    _name = 'payment_reseller.reseller'
    
    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
                    context={}, count=False, access_rights_uid=None):
    
            if context:
                if 'has_po' in context:
                    if context['has_po']:
                        res_pohead = self.pool.get('payment_reseller.po_head').search(cr, uid,[('reseller_id','!=', False)])
                        reseller_ids = []
                        for rec_pohead in res_pohead:
                            get_pohead = self.pool.get('payment_reseller.po_head').browse(cr, uid, rec_pohead)
                            reseller_ids.append(get_pohead.reseller_id.id)
                        args.append(("id","in",reseller_ids))
            
            return super(Reseller, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
                                            context=context, count=count, access_rights_uid=access_rights_uid)

    name =fields.Char(string="Fullname", required=True)
    address = fields.Char(string="Address")
    
class Prod(models.Model):
    _name = 'payment_reseller.products'
    
    name=fields.Char(string="Product Name", size= 50)
    unit = fields.Char(string="Unit", size=10)
    rs_price=fields.Float(string="Price")
    
    
class PO_Head(models.Model):
    _name = "payment_reseller.po_head"
    
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
        
        get_item_price = self.env['payment_reseller.products'].browse(item.id)
        self.price =   get_item_price.rs_price
        
        
    @api.model
    def create(self, vals):
        prod_id = vals['prod_id']
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
    overpaid = fields.Float(string="Over Payment" ,readonly=True)
    underpaid = fields.Float(string="Under Payment" ,readonly=True)
    outstanding = fields.Float(string="Outstanding Balance" ,readonly=True)
    Total = fields.Float(string="TOTAL", readonly = True, compute='_compute_total')
   
    @api.model
    def create(self, vals):
     # FOR INVOICE SEQUENCE   
        vals['or_num'] = self.env['ir.sequence'].get('or_code')
             
    # TO CREATE OUSTANDING ONCHANGE
        selected_reseller =  vals['rs_id']
        payment_list = self.env['payment_reseller.payment'].search([('rs_id','=',selected_reseller)],order='id desc',limit=1)
        for r in payment_list:
            vals['outstanding'] = r.underpaid * (-1)
            
#     TO CREATE UNDERPAID AND OVERPAID ONCHANGE   
        selected_invoice = vals['invoice_id']
        print 'selected_invoice', selected_invoice
        inv_list = self.env['payment_reseller.po_det'].search([('po_head_id','=',selected_invoice)])
         
        qty_price = 0.00
        total_pur = 0.00
        for r in inv_list:
            qty_price = (r.qty * r.price) - ((r.qty * r.price) * (r.discount/100))
            total_pur = total_pur + qty_price
            qty_price = 0.00

        selected_reseller =  vals['rs_id']
        payment_list = self.env['payment_reseller.payment'].search([('rs_id','=',selected_reseller)],order='id desc',limit=1)
        bal = 0.00
        for r in payment_list:
            bal = r.underpaid * (-1)

        pymt = vals['amt_render'] - (total_pur + bal)         

        print 'pymt', pymt
        if pymt > 0:
             vals['overpaid'] = pymt
        else:
             vals['underpaid'] = pymt
         
        return super(payment, self).create(vals)
    
    @api.onchange('rs_id')
    def _onchange_reseller(self):
        selected_reseller = self.rs_id.id
        inv_list = self.env['payment_reseller.po_head'].search([('reseller_id','=',selected_reseller)])
        payment_inv_list = self.search([('rs_id','=',selected_reseller)])
#         payment_inv_list = self.env['payment_reseller.payment'].browse(self.invoice_id)
        inv_lists= []
        p_inv_lists =[]
        for i in payment_inv_list:
            p_inv_lists.append(i.invoice_id.id)
        
     
        for r in inv_list:
            if r.id in p_inv_lists:
                print 'IN LIST'
                
            else:
                print 'NOT IN LIST'
                inv_lists.append(r.id)
        print '...',inv_lists
        return {'domain':{'invoice_id':[('id','in',inv_lists)]},}
    
    @api.onchange('amt_render')
    def _compute_payment(self):
#         selected_invoice =  self.invoice_id
#         
#         inv_list = self.env['payment_reseller.po_det'].search([('po_head_id','=',selected_invoice.id)])
#      
#         qty_price = 0.00
#         total_pur = 0.00
#         for r in inv_list:
#             qty_price = (r.qty * r.price) - ((r.qty * r.price) * (r.discount/100))
#             total_pur = total_pur + qty_price
#             qty_price = 0.00
        
        payment = self.amt_render - self.Total
        
        if payment > 0:
            self.overpaid = payment
        else:
            self.underpaid = payment
            
    @api.depends('invoice_id')
    def _compute_total(self):
        selected_invoice =  self.invoice_id
        
        inv_list = self.env['payment_reseller.po_det'].search([('po_head_id','=',selected_invoice.id)])
     
        qty_price = 0.00
        total_pur = 0.00
        for r in inv_list:
            qty_price = (r.qty * r.price) - ((r.qty * r.price) * (r.discount/100))
            total_pur = total_pur + qty_price + self.outstanding
            qty_price = 0.00
        self.Total = total_pur
        
    @api.onchange('rs_id')
    def _get_balance(self):
        selected_reseller =  self.rs_id
        payment_list = self.env['payment_reseller.payment'].search([('rs_id','=',selected_reseller.id)],order='id desc',limit=1)
        for r in payment_list:
            self.outstanding = r.underpaid * (-1)
            self.Total = self.outstanding
        
        