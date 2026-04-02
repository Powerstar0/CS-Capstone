from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Query
from models import (
    DepositRequest, WithdrawRequest, PortfolioHolding,
    HistoricalPortfolioResponse, HistoricalDataPoint,
)
from database import get_supabase_admin
from auth import get_current_user
from forex_service import get_historical_rates, PERIOD_MAP

router = APIRouter()


def _normalize_currency(currency: str) -> str:
    c = currency.upper().strip()
    if len(c) != 3:
        raise HTTPException(status_code=400, detail="Currency must be a 3-letter ticker (e.g. USD).")
    return c


@router.get("/", response_model=list[PortfolioHolding])
async def get_portfolio(current=Depends(get_current_user)):
    """Return all currency holdings for the authenticated user."""
    user_id = current["user"].id
    admin = get_supabase_admin()

    try:
        response = admin.table("portfolio").select("*").eq("id", user_id).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    holdings = []
    for row in response.data:
        holdings.append(PortfolioHolding(
            currency=row["currency-ticker-symbol"],
            amount=float(row["amount"] or 0),
        ))
    return holdings


@router.get("/history", response_model=HistoricalPortfolioResponse)
async def get_portfolio_history(
    period: str = Query("1mo", description="Time period: 1d, 1wk, 1mo, 3mo, 6mo, 1y, 3y, 5y"),
    current=Depends(get_current_user),
):
    """Return historical portfolio value in USD for the given time period."""
    if period not in PERIOD_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period '{period}'. Must be one of {list(PERIOD_MAP)}",
        )

    user_id = current["user"].id
    admin = get_supabase_admin()

    # Fetch current holdings
    try:
        response = admin.table("portfolio").select("*").eq("id", user_id).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    holdings = []
    for row in response.data:
        amt = float(row["amount"] or 0)
        if amt > 0:
            holdings.append({"currency": row["currency-ticker-symbol"], "amount": amt})

    if not holdings:
        return HistoricalPortfolioResponse(
            period=period,
            interval=PERIOD_MAP[period][1],
            data_points=[],
            currency="USD",
        )

    yf_period, yf_interval = PERIOD_MAP[period]

    # Fetch historical rates for each non-USD currency -> USD
    rate_series: dict[str, dict[str, float]] = {}  # currency -> {date -> rate}
    reference_dates: list[str] | None = None

    for h in holdings:
        ccy = h["currency"].upper()
        if ccy == "USD":
            continue
        try:
            data = get_historical_rates(ccy, "USD", period)
        except ValueError:
            # If we can't get rates for this currency, skip it
            continue

        date_rate_map = {pt["date"]: pt["rate"] for pt in data}
        rate_series[ccy] = date_rate_map

        # Use first non-USD currency's dates as reference
        if reference_dates is None:
            reference_dates = [pt["date"] for pt in data]

    # If all holdings are USD or no rate data returned, build a flat line
    usd_amount = sum(h["amount"] for h in holdings if h["currency"].upper() == "USD")
    if reference_dates is None:
        # All USD — generate synthetic date axis
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        # Simple: return a single data point at current value
        return HistoricalPortfolioResponse(
            period=period,
            interval=yf_interval,
            data_points=[HistoricalDataPoint(date=now.isoformat(), value=round(usd_amount, 2))],
            currency="USD",
        )

    # Build portfolio value at each date using forward-fill
    data_points: list[HistoricalDataPoint] = []
    last_known: dict[str, float] = {}  # currency -> last known rate

    for date_str in reference_dates:
        total = usd_amount  # USD holdings always contribute at 1:1

        for h in holdings:
            ccy = h["currency"].upper()
            if ccy == "USD":
                continue

            series = rate_series.get(ccy)
            if series is None:
                continue

            # Use rate for this date, or forward-fill from last known
            rate = series.get(date_str)
            if rate is not None:
                last_known[ccy] = rate
            else:
                rate = last_known.get(ccy)

            if rate is not None:
                total += h["amount"] * rate

        data_points.append(HistoricalDataPoint(date=date_str, value=round(total, 2)))

    return HistoricalPortfolioResponse(
        period=period,
        interval=yf_interval,
        data_points=data_points,
        currency="USD",
    )


@router.post("/deposit", response_model=PortfolioHolding)
async def deposit(body: DepositRequest, current=Depends(get_current_user)):
    """
    Add funds in a given currency to the user's portfolio.
    If a holding in that currency already exists its amount is increased.
    """
    user_id = current["user"].id
    currency = _normalize_currency(body.currency)
    admin = get_supabase_admin()

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive.")

    # Fetch existing holding for this user + currency
    try:
        existing = (
            admin.table("portfolio")
            .select("*")
            .eq("id", user_id)
            .eq("currency-ticker-symbol", currency)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if existing.data:
        current_amount = float(existing.data[0]["amount"] or 0)
        new_amount = current_amount + body.amount
        try:
            admin.table("portfolio").update({"amount": new_amount}).eq("id", user_id).eq(
                "currency-ticker-symbol", currency
            ).execute()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))
    else:
        try:
            admin.table("portfolio").insert({
                "id": user_id,
                "currency-ticker-symbol": currency,
                "amount": body.amount,
            }).execute()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

        new_amount = body.amount

    # Log the deposit
    now = datetime.now(timezone.utc)
    try:
        admin.table("transaction-log").insert({
            "sender_id": user_id,
            "receiver_id": user_id,
            "sender_currency_ticker_symbol": currency,
            "receiver_currency_ticker_symbol": currency,
            "sender-amount": body.amount,
            "receiver-amount": body.amount,
            "timestamp": now.isoformat(),
            "type": "DEPOSIT",
        }).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transaction log failed: {exc}")

    return PortfolioHolding(currency=currency, amount=new_amount)


@router.post("/withdraw", response_model=PortfolioHolding)
async def withdraw(body: WithdrawRequest, current=Depends(get_current_user)):
    """
    Withdraw funds in a given currency from the user's portfolio.
    Fails if the user has insufficient balance.
    """
    user_id = current["user"].id
    currency = _normalize_currency(body.currency)
    admin = get_supabase_admin()

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive.")

    # Fetch existing holding
    try:
        existing = (
            admin.table("portfolio")
            .select("*")
            .eq("id", user_id)
            .eq("currency-ticker-symbol", currency)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    current_amount = float(existing.data[0]["amount"] or 0) if existing.data else 0.0
    if current_amount < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds: have {current_amount} {currency}, need {body.amount}.",
        )

    new_amount = round(current_amount - body.amount, 8)
    try:
        admin.table("portfolio").update({"amount": new_amount}).eq("id", user_id).eq(
            "currency-ticker-symbol", currency
        ).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Log the withdrawal (negative amounts indicate outflow)
    now = datetime.now(timezone.utc)
    try:
        admin.table("transaction-log").insert({
            "sender_id": user_id,
            "receiver_id": user_id,
            "sender_currency_ticker_symbol": currency,
            "receiver_currency_ticker_symbol": currency,
            "sender-amount": -body.amount,
            "receiver-amount": -body.amount,
            "timestamp": now.isoformat(),
            "type": "WITHDRAW",
        }).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transaction log failed: {exc}")

    return PortfolioHolding(currency=currency, amount=new_amount)
