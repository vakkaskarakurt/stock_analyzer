"""
LSTM Model for stock price prediction.
Optimized for gold-based price prediction.
"""

import numpy as np
import os
import pickle
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping


class LSTMPredictor:
    """LSTM model for stock price prediction with gold normalization."""

    def __init__(
        self,
        lookback: int = 60,
        lstm_units: int = 50,
        dropout_rate: float = 0.2,
        learning_rate: float = 0.001
    ):
        self.lookback = lookback
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.model: Optional[Sequential] = None
        self.history = None

    def build_model(self) -> Sequential:
        """Build the LSTM neural network architecture - improved for better accuracy."""
        model = Sequential([
            # First LSTM layer with return sequences
            LSTM(
                units=self.lstm_units,
                return_sequences=True,
                input_shape=(self.lookback, 1)
            ),
            Dropout(self.dropout_rate),

            # Second LSTM layer
            LSTM(units=self.lstm_units, return_sequences=True),
            Dropout(self.dropout_rate),

            # Third LSTM layer
            LSTM(units=self.lstm_units // 2, return_sequences=False),
            Dropout(self.dropout_rate),

            # Dense layers
            Dense(units=50, activation='relu'),
            Dense(units=25, activation='relu'),
            Dense(units=1)  # Output layer
        ])

        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mean_squared_error',
            metrics=['mae']
        )

        self.model = model
        return model

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = 50,
        batch_size: int = 32,
        verbose: int = 1
    ) -> dict:
        """
        Train the LSTM model.

        Args:
            X_train: Training sequences (samples, lookback, 1)
            y_train: Training targets
            X_val: Validation sequences (optional)
            y_val: Validation targets (optional)
            epochs: Number of training epochs
            batch_size: Batch size for training
            verbose: Verbosity level (0, 1, or 2)

        Returns:
            Training history dictionary
        """
        if self.model is None:
            self.build_model()

        # Early stopping to prevent overfitting
        callbacks = [
            EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=10,
                restore_best_weights=True
            )
        ]

        # Prepare validation data
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)

        # Train the model
        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=verbose
        )

        return self.history.history

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the trained model.

        Args:
            X: Input sequences (samples, lookback, 1)

        Returns:
            Predicted values
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")

        return self.model.predict(X, verbose=0).flatten()

    def predict_future(
        self,
        last_sequence: np.ndarray,
        days: int = 30
    ) -> np.ndarray:
        """
        Predict future values iteratively.

        Args:
            last_sequence: Last known sequence (1, lookback, 1)
            days: Number of days to predict

        Returns:
            Array of predicted values for each future day
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")

        predictions = []
        current_sequence = last_sequence.copy()

        for _ in range(days):
            # Predict next value
            next_pred = self.model.predict(current_sequence, verbose=0)[0, 0]
            predictions.append(next_pred)

            # Update sequence: remove first, add prediction
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1, 0] = next_pred

        return np.array(predictions)

    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate model performance on test data.

        Returns:
            Dictionary with MSE, MAE, and MAPE metrics
        """
        if self.model is None:
            raise ValueError("Model not trained yet.")

        predictions = self.predict(X_test)

        # Calculate metrics
        mse = np.mean((predictions - y_test) ** 2)
        mae = np.mean(np.abs(predictions - y_test))

        # MAPE (avoid division by zero)
        non_zero_mask = y_test != 0
        mape = np.mean(np.abs((y_test[non_zero_mask] - predictions[non_zero_mask]) / y_test[non_zero_mask])) * 100

        # Directional accuracy
        if len(y_test) > 1:
            actual_direction = np.sign(np.diff(y_test))
            pred_direction = np.sign(np.diff(predictions))
            directional_acc = np.mean(actual_direction == pred_direction) * 100
        else:
            directional_acc = 0

        return {
            'mse': float(mse),
            'mae': float(mae),
            'mape': float(mape),
            'directional_accuracy': float(directional_acc)
        }

    def save(self, filepath: str):
        """Save the model to disk."""
        if self.model is None:
            raise ValueError("No model to save.")

        # Save Keras model
        self.model.save(f"{filepath}.keras")

        # Save metadata
        metadata = {
            'lookback': self.lookback,
            'lstm_units': self.lstm_units,
            'dropout_rate': self.dropout_rate,
            'learning_rate': self.learning_rate
        }
        with open(f"{filepath}_meta.pkl", 'wb') as f:
            pickle.dump(metadata, f)

    def load(self, filepath: str):
        """Load a saved model from disk."""
        self.model = load_model(f"{filepath}.keras")

        # Load metadata
        with open(f"{filepath}_meta.pkl", 'rb') as f:
            metadata = pickle.load(f)

        self.lookback = metadata['lookback']
        self.lstm_units = metadata['lstm_units']
        self.dropout_rate = metadata['dropout_rate']
        self.learning_rate = metadata['learning_rate']


class ModelCache:
    """Cache for trained models to avoid retraining."""

    def __init__(self, cache_dir: str = "model_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.models: Dict[str, LSTMPredictor] = {}
        self.scalers: Dict[str, Any] = {}
        self.last_trained: Dict[str, datetime] = {}

    def get_cache_key(self, symbol: str, lookback: int) -> str:
        """Generate cache key for a model."""
        return f"{symbol}_{lookback}"

    def is_cached(self, symbol: str, lookback: int, max_age_hours: int = 24) -> bool:
        """Check if a valid cached model exists."""
        key = self.get_cache_key(symbol, lookback)

        # Check in-memory cache
        if key in self.models:
            if key in self.last_trained:
                age = datetime.now() - self.last_trained[key]
                if age.total_seconds() < max_age_hours * 3600:
                    return True

        # Check disk cache
        model_path = os.path.join(self.cache_dir, key)
        if os.path.exists(f"{model_path}.keras"):
            # TODO: Check file age
            return True

        return False

    def get(self, symbol: str, lookback: int) -> Tuple[Optional[LSTMPredictor], Optional[Any]]:
        """Get cached model and scaler."""
        key = self.get_cache_key(symbol, lookback)

        # Try in-memory cache first
        if key in self.models:
            return self.models[key], self.scalers.get(key)

        # Try disk cache
        model_path = os.path.join(self.cache_dir, key)
        if os.path.exists(f"{model_path}.keras"):
            predictor = LSTMPredictor(lookback=lookback)
            predictor.load(model_path)

            # Load scaler
            scaler = None
            scaler_path = f"{model_path}_scaler.pkl"
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)

            self.models[key] = predictor
            self.scalers[key] = scaler
            return predictor, scaler

        return None, None

    def set(
        self,
        symbol: str,
        lookback: int,
        predictor: LSTMPredictor,
        scaler: Any
    ):
        """Cache a trained model."""
        key = self.get_cache_key(symbol, lookback)

        # In-memory cache
        self.models[key] = predictor
        self.scalers[key] = scaler
        self.last_trained[key] = datetime.now()

        # Disk cache
        model_path = os.path.join(self.cache_dir, key)
        predictor.save(model_path)

        # Save scaler
        with open(f"{model_path}_scaler.pkl", 'wb') as f:
            pickle.dump(scaler, f)
