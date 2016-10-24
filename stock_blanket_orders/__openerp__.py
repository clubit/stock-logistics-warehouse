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
{
    'name': 'Stock Blanket Orders',
    'version': '0.1',
    'author': 'Clubit BVBA',
    'maintainer': 'Clubit BVBA',
    'website': 'https://clubit.be',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'summary': "Extend picking view with fields that allow blanket orders to run efficiently",
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_picking.xml',
        'views/report_forecast.xml'
    ],
    'installable': True,
    'application': False,
}
