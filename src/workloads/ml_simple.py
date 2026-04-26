# src/workloads/ml_simple.py - NEW FILE
import numpy as np
import logging
from sklearn.linear_model import LinearRegression
from src.utils.logger import log_execution

logger = logging.getLogger(__name__)

# Train model ONCE at module load (100k samples)
logger.info("Training ML model...")
X_train = np.random.rand(100_000, 10)
y_train = X_train.sum(axis=1) + np.random.randn(100_000) * 0.1
_model = LinearRegression()
_model.fit(X_train, y_train)
logger.info("ML model trained and ready.")

@log_execution
def predict_batch(n_samples: int) -> float:
    """Predict only (no training). Param range: 1000-10000 samples."""
    X_test = np.random.rand(n_samples, 10)
    predictions = _model.predict(X_test)
    return float(predictions.mean())