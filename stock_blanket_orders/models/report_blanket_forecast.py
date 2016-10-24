from openerp import models, fields, SUPERUSER_ID, api, tools
from openerp.osv import osv

class report_blanket_forecast(osv.Model):
    _name = "report.blanket.forecast"
    _description = "Blanket Orders Forecasted Stock Report" 
    _auto = False

    id = fields.Integer('ID', readonly=True)
    product_product = fields.Char('Product')
    current_stock = fields.Float('Current Stock')
    incoming_stock = fields.Float('Incoming')
    outgoing_stock = fields.Float('Outgoing')
    forecasted_stock = fields.Float('Forecast')

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW report_blanket_forecast AS (

    WITH t1 AS (
      SELECT sum(qty) AS current_stock, product_id FROM stock_quant
      WHERE location_id = 59
      GROUP BY product_id
    ),
    t2 AS (
      SELECT sum(infc.product_uom_qty) incoming_stock, infc.product_id FROM stock_move infc 
      WHERE infc.location_dest_id = 59 AND infc.state NOT IN ('done','cancel')
      GROUP BY infc.product_id
    ),
    t3 AS (
      SELECT sum(outfc.product_uom_qty) outgoing_stock, outfc.product_id FROM stock_move outfc 
      WHERE outfc.location_id = 59 AND outfc.state NOT IN ('done','cancel')
      GROUP BY outfc.product_id
    ),
    t4 AS (
      SELECT prod.id, prod.name_template AS product_product FROM product_product prod
    ) 
    SELECT t4.id as id, product_product, coalesce(current_stock,0) AS current_stock, coalesce(incoming_stock,0) AS incoming_stock, coalesce(outgoing_stock,0) AS outgoing_stock, coalesce(current_stock,0) + coalesce(incoming_stock,0) - coalesce(outgoing_stock,0) AS forecasted_stock
    FROM t4 
    FULL OUTER JOIN t2 ON t4.id = t2.product_id
    FULL OUTER JOIN t3 ON t4.id = t3.product_id
    FULL OUTER JOIN t1 ON t4.id = t1.product_id
    WHERE coalesce(current_stock,0) + coalesce(incoming_stock,0) - coalesce(outgoing_stock,0) != 0.0)""")
    
    # report_blanket_forecast()

