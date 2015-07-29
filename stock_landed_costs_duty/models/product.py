from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

SPLIT_METHOD = [
    ('equal', 'Equal'),
    ('by_quantity', 'By Quantity'),
    ('by_current_cost_price', 'By Current Cost Price'),
    ('by_weight', 'By Weight'),
    ('by_volume', 'By Volume'),
    ('by_duty', 'By Duty'),
]

class product_template(models.Model):
    _inherit = "product.template"

    duty = fields.Float(digits=dp.get_precision('Landed Cost'))
    split_method = fields.Selection(SPLIT_METHOD)
