import os
import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel
from .preprocess import Scaler


class WingSurrogate:
    def __init__(self):
        kernel = ConstantKernel(1.0) * RBF(length_scale=1.0)
        self.model = GaussianProcessRegressor(
            kernel=kernel,
            alpha=1e-4,
            normalize_y=True
        )
        self.scaler = Scaler()
        self.trained = False

    def load_and_train(self, csv_path=None):
        if csv_path is None:
            base_dir = os.path.dirname(__file__)
            csv_path = os.path.join(base_dir, "cad_summary.csv")

        df = pd.read_csv(csv_path)

        # Inputs: geometry (Category A)
        X = df[["wingspan", "wing_rib_chord"]].values

        # Target: wing weight (grams)
        y = df["wing_weight"].values

        self.scaler.fit(X)
        Xn = self.scaler.transform(X)
        self.model.fit(Xn, y)

        self.trained = True

    def predict(self, wingspan, wing_chord):
        if not self.trained:
            raise RuntimeError("WingSurrogate used before training.")

        X = np.array([[wingspan, wing_chord]])
        Xn = self.scaler.transform(X)
        return float(self.model.predict(Xn)[0])
