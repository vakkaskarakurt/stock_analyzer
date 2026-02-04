"""
FastAPI service for LSTM stock price prediction.
Predicts stock prices in gold-denominated terms for inflation-adjusted forecasting.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import numpy as np

from data_processor import DataProcessor
from model import LSTMPredictor, ModelCache


# Initialize FastAPI app
app = FastAPI(
    title="Stock Prediction API",
    description="LSTM-based stock price prediction with gold normalization",
    version="1.0.0"
)

# CORS middleware for .NET backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5035", "http://localhost:4200", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
data_processor = DataProcessor()
model_cache = ModelCache()


# Request/Response models
class PredictionRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., THYAO)")
    days: int = Field(default=30, ge=1, le=90, description="Number of days to predict")
    lookback: int = Field(default=60, ge=30, le=120, description="Historical window size")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "THYAO",
                "days": 30,
                "lookback": 60
            }
        }


class PredictionPoint(BaseModel):
    date: str
    price_gold: float
    price_usd: float
    price_try: Optional[float] = None


class HistoricalPoint(BaseModel):
    date: str
    price_gold: float
    price_usd: float


class PredictionResponse(BaseModel):
    symbol: str
    predictions: List[PredictionPoint]
    historical: List[HistoricalPoint]
    confidence: float
    trend: str  # "up", "down", "neutral"
    model_info: str
    last_price_usd: float
    last_price_gold: float
    predicted_change_percent: float


class HealthResponse(BaseModel):
    status: str
    timestamp: str


# Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_stock(request: PredictionRequest):
    """
    Predict future stock prices using LSTM model.

    The model:
    1. Converts historical prices to gold-denominated values
    2. Trains/loads LSTM model
    3. Predicts future values in gold terms
    4. Converts back to USD for display
    """
    try:
        symbol = request.symbol.upper()
        days = request.days
        lookback = request.lookback

        # Check cache for existing model
        cached_model, cached_scaler = model_cache.get(symbol, lookback)

        if cached_model is not None and cached_scaler is not None:
            # Use cached model
            predictor = cached_model

            # Get fresh data for prediction
            pred_data = data_processor.process_for_prediction(symbol, lookback)
            data_processor.scaler = cached_scaler

        else:
            # Train new model
            print(f"Training new model for {symbol}...")

            # Prepare training data
            train_data = data_processor.process_for_training(
                symbol,
                lookback=lookback,
                train_split=0.8
            )

            # Build and train model - improved parameters
            predictor = LSTMPredictor(
                lookback=lookback,
                lstm_units=100,
                dropout_rate=0.3,
                learning_rate=0.001
            )
            predictor.build_model()

            history = predictor.train(
                X_train=train_data['X_train'],
                y_train=train_data['y_train'],
                X_val=train_data['X_test'],
                y_val=train_data['y_test'],
                epochs=100,
                batch_size=16,
                verbose=0
            )

            # Cache the model
            model_cache.set(symbol, lookback, predictor, data_processor.scaler)

            # Get prediction data
            pred_data = data_processor.process_for_prediction(symbol, lookback)

        # Make predictions
        predictions_scaled = predictor.predict_future(
            pred_data['last_sequence'],
            days=days
        )

        # Convert predictions back to real values
        prices_gold, prices_usd = data_processor.inverse_transform(
            predictions_scaled,
            pred_data['last_gold_price']
        )

        # Generate prediction dates (skip weekends)
        prediction_dates = []
        current_date = datetime.now()
        while len(prediction_dates) < days:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                prediction_dates.append(current_date.strftime('%Y-%m-%d'))

        # Build prediction points
        predictions = []
        for i, date in enumerate(prediction_dates):
            predictions.append(PredictionPoint(
                date=date,
                price_gold=float(prices_gold[i]),
                price_usd=float(prices_usd[i])
            ))

        # Build historical points
        historical = []
        hist_data = pred_data['historical']
        for idx, row in hist_data.iterrows():
            historical.append(HistoricalPoint(
                date=row['Date'],
                price_gold=float(row['Close_Gold']),
                price_usd=float(row['Close'])
            ))

        # Calculate metrics
        last_price = pred_data['last_stock_price']
        last_pred = prices_usd[-1]
        change_percent = ((last_pred - last_price) / last_price) * 100

        # Determine trend
        if change_percent > 2:
            trend = "up"
        elif change_percent < -2:
            trend = "down"
        else:
            trend = "neutral"

        # Calculate confidence based on actual model performance
        try:
            train_data = data_processor.process_for_training(symbol, lookback=lookback, train_split=0.8)
            metrics = predictor.evaluate(train_data['X_test'], train_data['y_test'])
            # Confidence = 100 - MAPE (capped between 0.3 and 0.95)
            confidence = min(0.95, max(0.30, (100 - metrics['mape']) / 100))
        except:
            confidence = 0.5

        return PredictionResponse(
            symbol=symbol,
            predictions=predictions,
            historical=historical,
            confidence=round(confidence, 2),
            trend=trend,
            model_info=f"LSTM-{lookback}-{days}",
            last_price_usd=float(last_price),
            last_price_gold=float(pred_data['last_stock_price_gold']),
            predicted_change_percent=round(change_percent, 2)
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/symbols/{symbol}/info")
async def get_symbol_info(symbol: str):
    """Get basic info about a stock symbol."""
    try:
        symbol = symbol.upper()

        # Add .IS suffix if needed
        yahoo_symbol = symbol if '.' in symbol else f"{symbol}.IS"

        import yfinance as yf
        ticker = yf.Ticker(yahoo_symbol)
        info = ticker.info

        return {
            "symbol": symbol,
            "name": info.get("shortName", "Unknown"),
            "currency": info.get("currency", "TRY"),
            "exchange": info.get("exchange", "IST"),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", 0))
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Symbol not found: {symbol}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
