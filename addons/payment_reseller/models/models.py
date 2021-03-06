# -*- coding: utf-8 -*-

from openerp import api, fields, models
from datetime import datetime, timedelta
import time
from methods import _create_payment
from methods import _get_total

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
    _order = 'po_date desc'
    
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
    _order = 'id desc'
     
    name = fields.Char(string ="Name", related ="or_num")
    payment_date = fields.Date(string="Date", default = lambda *a: time.strftime('%Y-%m-%d'))
    or_num =fields.Char(string="Receipt", readonly=True)
    rs_id = fields.Many2one('payment_reseller.reseller', string='Reseller')
    invoice_id = fields.Many2one('payment_reseller.po_head', string="Invoice")
    prods = fields.One2many(related="invoice_id.prod_name", readonly = True)
    amt_render = fields.Float(string="Amount Render", digits =(16,2))
    overpaid = fields.Float(string="Over Payment" ,readonly=True, digits =(16,2))
    underpaid = fields.Float(string="Under Payment" ,readonly=True, digits =(16,2))
    outstanding = fields.Float(string="Outstanding Balance" ,readonly=True, digits =(16,2))
    Total = fields.Float(string="TOTAL", readonly = True, compute='_compute_total', digits= (16,2))
    color = fields.Integer()
    sum_rep = fields.Many2one('payment_reseller.report_handler', ondelete="cascade")
    
    @api.model
    def create(self, vals):
     # FOR INVOICE SEQUENCE   
        vals['or_num'] = self.env['ir.sequence'].get('or_code')
             
    # TO CREATE OUSTANDING ONCHANGE
    
        _create_payment(self,vals)
   
        return super(payment, self).create(vals)
    
    @api.multi   
    def write(self, vals):
        if 'amt_render' in vals:
            vals['amt_render'] = vals.get('amt_render')
            
            
            computed_total = _get_total(self)
            p = vals['amt_render'] - computed_total
          
            if p > 0:
                vals['overpaid'] = p
            elif p < 0:
                vals['underpaid'] = p
            else:
                vals['overpaid'] = 0.00
                vals['underpaid'] = 0.00
                
        res_id = super(payment, self).write(vals)
          
        return res_id 
     
    @api.onchange('rs_id')
    def _onchange_reseller(self):
        selected_reseller = self.rs_id.id
        inv_list = self.env['payment_reseller.po_head'].search([('reseller_id','=',selected_reseller)])
        payment_inv_list = self.search([('rs_id','=',selected_reseller)])

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
        return {'domain':{'invoice_id':[('id','in',inv_lists)]},}
    
    @api.onchange('amt_render')
    def _compute_payment(self):
        
        payment = self.amt_render - self.Total
        
        if payment > 0:
            self.overpaid = payment
        elif payment < 0 :
            self.underpaid = payment
        else:
            self.overpaid = 0.00
            self.underpaid = 0.00
            
    @api.depends('invoice_id')
    def _compute_total(self):
        selected_invoice =  self.invoice_id
        
        inv_list = self.env['payment_reseller.po_det'].search([('po_head_id','=',selected_invoice.id)])
     
        qty_price = 0.00
        total_pur = 0.00
        for r in inv_list:
            qty_price = (r.qty * r.price) - ((r.qty * r.price) * (r.discount/100))
            total_pur = total_pur + qty_price
        
            qty_price = 0.00
       
        self.Total = total_pur + (self.outstanding)
        
    @api.onchange('rs_id')
    def _get_balance(self):
        selected_reseller =  self.rs_id
        payment_list = self.env['payment_reseller.payment'].search([('rs_id','=',selected_reseller.id)],order='id desc',limit=1)
        for r in payment_list:
            if r.underpaid != 0:
                self.outstanding = r.underpaid * (-1)
                self.Total = self.outstanding
            elif r.overpaid != 0:
                self.outstanding = r.overpaid * (-1)
                self.Total = self.outstanding
        