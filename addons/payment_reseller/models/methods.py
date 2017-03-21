from openerp import models, fields, api, SUPERUSER_ID
from datetime import datetime
from openerp.exceptions import ValidationError

def _create_payment(self, vals):
    
        selected_reseller =  vals['rs_id']
        payment_list = self.env['payment_reseller.payment'].search([('rs_id','=',selected_reseller)],order='id desc',limit=1)
        for r in payment_list:
            if r.underpaid != 0:
                vals['outstanding'] = r.underpaid * (-1)
            else:
                vals['outstanding'] = r.overpaid * (-1)
             
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
 
        print 'total_pur...',total_pur
        selected_reseller =  vals['rs_id']
        payment_list = self.env['payment_reseller.payment'].search([('rs_id','=',selected_reseller)],order='id desc',limit=1)
        bal = 0.00
        for r in payment_list:
            if r.underpaid != 0:
                bal = r.underpaid * (-1)
            else:
                bal = r.overpaid * (-1)
                 
        pymt = vals['amt_render'] - (total_pur + (bal))         
        print 'total_pur', total_pur
        print 'bal', bal
        print 'pymt', pymt
        if pymt > 0:
             vals['overpaid'] = pymt
        else:
             vals['underpaid'] = pymt
        
        
def _get_total(self):
        selected_invoice =  self.invoice_id
         
        print '>>>', selected_invoice
        inv_list = self.env['payment_reseller.po_det'].search([('po_head_id','=',selected_invoice.id)])
      
        qty_price = 0.00
        total_pur = 0.00
        for r in inv_list:
            qty_price = (r.qty * r.price) - ((r.qty * r.price) * (r.discount/100))
            total_pur = total_pur + qty_price
             
            print 'price*qty', qty_price
            print '...', total_pur
            qty_price = 0.00
        
        c_total = total_pur + (self.outstanding)
        
        return round(c_total,2)