{
    'name': 'POS Utilidad y Margen',
    'version': '17.0.1.0.0',
    'summary': 'Cálculo automático de utilidad y margen en el Punto de Venta',
    'description': """
POS Utilidad y Margen

Este módulo agrega el cálculo automático de la utilidad en las ventas
realizadas desde el Punto de Venta (POS).

Funcionalidades principales:
- Cálculo automático del costo total por orden POS
- Utilidad = Total de la venta - Costo total
- Visualización de la utilidad directamente en la orden POS
- Consolidación de la utilidad en los movimientos contables (facturas)
- Compatible con Odoo 17

Desarrollado por JMA
    """,
    'category': 'Point of Sale',
    'author': 'JMA',
    'website': 'https://fsf3cj7zbi8.cloudpepper.site/',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'account',
        'pos_hr',
    ],
    'data': [
        'views/pos_order_view.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
