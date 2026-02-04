"""
Data processor for LSTM stock prediction.
Handles data fetching, gold conversion, and preprocessing.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, Optional


class DataProcessor:
    """Processes stock data for LSTM prediction with gold-based normalization."""

    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.gold_scaler = MinMaxScaler(feature_range=(0, 1))

    def fetch_stock_data(self, symbol: str, years: int = 3) -> pd.DataFrame:
        """
        Fetch historical stock data from Yahoo Finance.
        Automatically appends .IS suffix for BIST stocks.
        """
        # Add .IS suffix for BIST stocks if not present
        if '.' not in symbol and '-' not in symbol:
            symbol = f"{symbol}.IS"

        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            raise ValueError(f"No data found for symbol: {symbol}")

        return df[['Open', 'High', 'Low', 'Close', 'Volume']]

    def fetch_gold_data(self, years: int = 3) -> pd.DataFrame:
        """Fetch gold price data (GC=F) from Yahoo Finance."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        ticker = yf.Ticker("GC=F")
        df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            raise ValueError("Could not fetch gold data")

        return df[['Close']].rename(columns={'Close': 'Gold'})

    def convert_to_gold(self, stock_df: pd.DataFrame, gold_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert stock prices to gold-denominated values.
        This removes inflation effects and shows real value.
        """
        # Remove timezone info for alignment
        stock_df = stock_df.copy()
        gold_df = gold_df.copy()

        stock_df.index = stock_df.index.tz_localize(None)
        gold_df.index = gold_df.index.tz_localize(None)

        # Normalize to date only (remove time component)
        stock_df.index = stock_df.index.normalize()
        gold_df.index = gold_df.index.normalize()

        # Align dates
        merged = stock_df.join(gold_df, how='inner')

        if merged.empty:
            raise ValueError("No overlapping dates between stock and gold data")

        # Convert all OHLC values to gold terms
        for col in ['Open', 'High', 'Low', 'Close']:
            merged[f'{col}_Gold'] = merged[col] / merged['Gold']

        return merged

    def prepare_sequences(
        self,
        data: np.ndarray,
        lookback: int = 60
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training.
        Uses sliding window approach.

        Args:
            data: Normalized price data
            lookback: Number of past days to use for prediction

        Returns:
            X: Input sequences (samples, lookback, features)
            y: Target values (samples,)
        """
        X, y = [], []

        for i in range(lookback, len(data)):
            X.append(data[i-lookback:i])
            y.append(data[i])

        return np.array(X), np.array(y)

    def process_for_training(
        self,
        symbol: str,
        lookback: int = 60,
        train_split: float = 0.8
    ) -> dict:
        """
        Full pipeline to prepare data for LSTM training.

        Returns:
            Dictionary with training and test data, scalers, and metadata
        """
        # Fetch data
        stock_df = self.fetch_stock_data(symbol)
        gold_df = self.fetch_gold_data()

        # Convert to gold terms
        merged = self.convert_to_gold(stock_df, gold_df)

        # Use Close price in gold terms
        gold_prices = merged['Close_Gold'].values.reshape(-1, 1)

        # Scale to 0-1 range
        scaled_data = self.scaler.fit_transform(gold_prices)

        # Create sequences
        X, y = self.prepare_sequences(scaled_data.flatten(), lookback)

        # Reshape X for LSTM: (samples, timesteps, features)
        X = X.reshape((X.shape[0], X.shape[1], 1))

        # Split into train/test
        split_idx = int(len(X) * train_split)

        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Get dates for reference
        dates = merged.index[lookback:]
        train_dates = dates[:split_idx]
        test_dates = dates[split_idx:]

        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'train_dates': train_dates,
            'test_dates': test_dates,
            'scaler': self.scaler,
            'last_sequence': X[-1:],  # For future predictions
            'last_gold_price': merged['Gold'].iloc[-1],
            'last_stock_price': merged['Close'].iloc[-1],
            'symbol': symbol
        }

    def process_for_prediction(
        self,
        symbol: str,
        lookback: int = 60
    ) -> dict:
        """
        Prepare data for making predictions (no train/test split).

        Returns:
            Dictionary with scaled data and metadata for prediction
        """
        # Fetch data
        stock_df = self.fetch_stock_data(symbol)
        gold_df = self.fetch_gold_data()

        # Convert to gold terms
        merged = self.convert_to_gold(stock_df, gold_df)

        # Use Close price in gold terms
        gold_prices = merged['Close_Gold'].values.reshape(-1, 1)

        # Scale to 0-1 range
        scaled_data = self.scaler.fit_transform(gold_prices)

        # Get last sequence for prediction
        last_sequence = scaled_data[-lookback:].reshape(1, lookback, 1)

        # Historical data for context
        historical = merged.tail(lookback).copy()
        historical['Date'] = historical.index.strftime('%Y-%m-%d')

        return {
            'last_sequence': last_sequence,
            'scaler': self.scaler,
            'last_gold_price': merged['Gold'].iloc[-1],
            'last_stock_price': merged['Close'].iloc[-1],
            'last_stock_price_gold': merged['Close_Gold'].iloc[-1],
            'historical': historical,
            'all_scaled_data': scaled_data,
            'symbol': symbol,
            'lookback': lookback
        }

    def inverse_transform(
        self,
        scaled_predictions: np.ndarray,
        gold_price: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert scaled predictions back to real values.

        Returns:
            Tuple of (prices_in_gold, prices_in_usd)
        """
        # Reshape for inverse transform
        scaled_predictions = scaled_predictions.reshape(-1, 1)

        # Get gold-denominated prices
        prices_in_gold = self.scaler.inverse_transform(scaled_predictions).flatten()

        # Convert to USD (using last known gold price as estimate)
        prices_in_usd = prices_in_gold * gold_price

        return prices_in_gold, prices_in_usd
