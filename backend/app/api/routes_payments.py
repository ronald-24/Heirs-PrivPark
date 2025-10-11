from __future__ import annotations

import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import verify_bearer_token_and_get_user
from app.db.session import get_db
from app.db.repositories.booking_repo import (
    get_booking,
    create_payment,
    attach_checkout_session,
    mark_booking_confirmed,
)
from app.db.models import PaymentStatus
from app.schemas.booking import PaymentCreateSession, CheckoutSessionOut
from app.services.notification_service import NotificationService


router = APIRouter(prefix="/payments", tags=["payments"])


def _get_stripe():
    try:
        import stripe  # type: ignore
    except Exception:
        raise HTTPException(status_code=500, detail="Stripe SDK not installed")
    secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not secret_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    stripe.api_key = secret_key
    return stripe


@router.post("/create-checkout-session", response_model=CheckoutSessionOut)
def create_checkout_session(
    payload: PaymentCreateSession,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    booking = get_booking(db, payload.booking_id)
    if not booking or booking.user_id != user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    stripe = _get_stripe()

    session = stripe.checkout.Session.create(
        mode="payment",
        success_url=payload.success_url,
        cancel_url=payload.cancel_url,
        line_items=[
            {
                "price_data": {
                    "currency": booking.currency,
                    "product_data": {"name": f"Parking #{booking.parking_space_id}"},
                    "unit_amount": int(round(booking.total_amount * 100)),
                },
                "quantity": 1,
            }
        ],
        metadata={"booking_id": str(booking.id)},
    )

    attach_checkout_session(db, booking.id, session.id)
    return CheckoutSessionOut(checkout_url=session.url)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    stripe = _get_stripe()
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    event = None
    try:
        if webhook_secret and sig_header:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret)
        else:
            event = stripe.Event.construct_from(request.json(), stripe.api_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")

    if event and event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        booking_id = int(session.get("metadata", {}).get("booking_id", 0))
        if booking_id:
            mark_booking_confirmed(db, booking_id)
            # Record payment
            payment_intent_id = session.get("payment_intent")
            receipt_url = None
            try:
                if payment_intent_id:
                    pi = stripe.PaymentIntent.retrieve(payment_intent_id)
                    charges = pi.get("charges", {}).get("data", [])
                    if charges:
                        receipt_url = charges[0].get("receipt_url")
            except Exception:
                receipt_url = None

            booking = get_booking(db, booking_id)
            if booking:
                payment = create_payment(
                    db,
                    user_id=booking.user_id,
                    parking_space_id=booking.parking_space_id,
                    booking_id=booking.id,
                    amount=booking.total_amount,
                    currency=booking.currency,
                    payment_date=datetime.now(timezone.utc),
                    provider_payment_id=str(
                        payment_intent_id) if payment_intent_id else None,
                    status=PaymentStatus.complet,
                    receipt_url=receipt_url,
                )

                # Create a payment confirmation notification
                try:
                    NotificationService.create_payment_confirmation_notification(
                        db, payment, booking.user)
                except Exception as e:
                    # Log the error but don't fail the payment process
                    print(
                        f"Error creating payment notification: {e}")

    return {"received": True}
