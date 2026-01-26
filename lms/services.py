import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(name, description):
    """
    Создает продукт в Stripe.
    :param name: Название продукта
    :param description: Описание продукта
    :return: ID созданного продукта
    """
    product = stripe.Product.create(name=name, description=description)
    return product.id


def create_stripe_price(product_id, amount, currency="usd"):
    """
    Создает цену для продукта в Stripe.
    :param product_id: ID продукта в Stripe
    :param amount: Стоимость в копейках/центах (умноженная на 100)
    :param currency: Валюта (по умолчанию 'usd')
    :return: ID созданной цены
    """
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,
        currency=currency,
    )
    return price.id


def create_stripe_checkout_session(price_id, success_url, cancel_url):
    """
    Создает сессию оплаты в Stripe.
    :param price_id: ID цены в Stripe
    :param success_url: URL для перенаправления после успешной оплаты
    :param cancel_url: URL для перенаправления при отмене оплаты
    :return: Объект сессии (содержит URL для оплаты)
    """
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session
