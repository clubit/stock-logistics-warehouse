# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2016 Clubit BVBA
#    (<https://clubit.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, SUPERUSER_ID, api

class StockPicking(models.Model):
    """
    add fields.
    """
    _inherit = 'stock.picking'

    is_loaded = fields.Boolean('Is Loaded')
    is_shipped = fields.Boolean('Is Shipped')
    show_cbm = fields.Boolean('Show CBM')
    cbm_total = fields.Float(compute='_cal_cbm', store=True)
    date_etd = fields.Datetime('ETD')

    @api.depends('product_id', 'move_lines')
    def _cal_cbm(self):
        for picking in self:
            picking.cbm_total = sum((move.product_id.volume*move.product_uom_qty) for move in picking.move_lines if move.state != 'cancel')

#todo add stock_move model with cbm

class StockMove(models.Model):
    """
    add fields.
    """
    _inherit = 'stock.move'

    cbm_move = fields.Float(compute='_cal_move_volume', store=True)

    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def _cal_move_volume(self):
        for move in self.filtered(lambda moves: moves.product_id.volume > 0.00):
            move.cbm_move = (move.product_qty * move.product_id.volume)
