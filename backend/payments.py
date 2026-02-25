import stripe
from config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, FRONTEND_URL

stripe.api_key = STRIPE_SECRET_KEY


def create_checkout_session(
    amount_cents: int,
    tip_cents: int,
    receiver_name: str,
    transaction_id: str,
    success_url: str = None,
    cancel_url: str = None,
) -> stripe.checkout.Session:
    if success_url is None:
        success_url = f"{FRONTEND_URL}/success.html"
    if cancel_url is None:
        cancel_url = f"{FRONTEND_URL}/cancel.html"
    line_items = [
        {
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Meal gift for {receiver_name}"},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }
    ]

    if tip_cents > 0:
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Platform tip — thank you!"},
                    "unit_amount": tip_cents,
                },
                "quantity": 1,
            }
        )

    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        metadata={"transaction_id": transaction_id},
    )


def construct_webhook_event(payload: bytes, sig_header: str):
    return stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
