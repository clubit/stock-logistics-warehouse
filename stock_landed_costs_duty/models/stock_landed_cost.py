from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare, float_round

import product

class stock_landed_cost(models.Model):
    _inherit = "stock.landed.cost"

    @api.multi
    def get_valuation_lines(self, picking_ids=None):
        lines = super(stock_landed_cost, self).get_valuation_lines(picking_ids=picking_ids)
        picking_obj = self.env['stock.picking']
        if not picking_ids:
            return lines
        for picking in picking_obj.browse(picking_ids):
            for move in picking.move_lines:
                # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
                if move.product_id.valuation != 'real_time' or move.product_id.cost_method != 'real':
                    continue
                for line in lines:  # update the correct line with the duty amount
                    if not line['move_id'] == move.id:
                        continue
                    line.update({'duty': move.product_id and move.product_id.duty})
        return lines

    @api.multi
    def calculate_duty(self):
        def ref(module, xml_id):
            proxy = self.env['ir.model.data']
            return proxy.get_object_reference(module, xml_id)
        total_duty = 0.0
        for cost in self:
            for picking in cost.picking_ids:
                for move in picking.move_lines:
                    #it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
                    if move.product_id.valuation != 'real_time' or move.product_id.cost_method != 'real':
                        continue
                    for quant in move.quant_ids:
                        total_duty += quant.qty * quant.cost * ((move.product_id and move.product_id.duty) or 0.0)

            # create duty line
            product_model, product_id = ref('stock_landed_costs_duty', 'product_product_duty')
            product = self.env[product_model].browse(product_id)
            self.env['stock.landed.cost.lines'].create({
                'name': product.name,
                'cost_id': cost.id,
                'product_id': product.id,
                'price_unit': total_duty,
                'split_method': product.split_method,
                'account_id': product.property_account_expense and product.property_account_expense.id or product.categ_id.property_account_expense_categ.id
            })
        return True

    def compute_landed_cost(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('stock.valuation.adjustment.lines')
        unlink_ids = line_obj.search(cr, uid, [('cost_id', 'in', ids)], context=context)
        line_obj.unlink(cr, uid, unlink_ids, context=context)
        digits = dp.get_precision('Product Price')(cr)
        towrite_dict = {}
        for cost in self.browse(cr, uid, ids, context=None):
            if not cost.picking_ids:
                continue
            picking_ids = [p.id for p in cost.picking_ids]
            total_qty = 0.0
            total_cost = 0.0
            total_duty = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            vals = self.get_valuation_lines(cr, uid, [cost.id], picking_ids=picking_ids, context=context)
            for v in vals:
                for line in cost.cost_lines:
                    v.update({'cost_id': cost.id, 'cost_line_id': line.id})
                    self.pool.get('stock.valuation.adjustment.lines').create(cr, uid, v, context=context)
                total_qty += v.get('quantity', 0.0)
                total_cost += v.get('former_cost', 0.0)
                total_duty += total_cost * v.get('duty', 0.0)
                total_weight += v.get('weight', 0.0)
                total_volume += v.get('volume', 0.0)
                total_line += 1

            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        elif line.split_method == 'by_duty' and total_cost:
                            per_unit = (line.price_unit / total_duty)
                            value = valuation.duty * per_unit
                        else:
                            value = (line.price_unit / total_line)

                        if digits:
                            value = float_round(value, precision_digits=digits[1], rounding_method='UP')
                            value = min(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        if towrite_dict:
            for key, value in towrite_dict.items():
                line_obj.write(cr, uid, key, {'additional_landed_cost': value}, context=context)
        return True

class stock_landed_cost_lines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    split_method = fields.Selection(product.SPLIT_METHOD)

class stock_valuation_adjustment_lines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    duty = fields.Float(digits=dp.get_precision('Landed Cost'))
