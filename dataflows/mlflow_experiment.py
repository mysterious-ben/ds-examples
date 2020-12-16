"""
Pipeline for the notebook `mlflow_experiment.ipynb`
"""

from time import sleep
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, make_scorer
from sklearn.model_selection import KFold, cross_validate
# from sklearn.linear_model import LinearRegression
import dutil.pipeline as dpipe
import warnings
from loguru import logger
from pathlib import Path
import mlflow
import mlflow.sklearn
# import mlflow.lightgbm
# from typing import Tuple

# MLFlow throws user warnings in Jupyter
warnings.filterwarnings('ignore', category=DeprecationWarning)


PREFIX = 'mlpipe_'
# MLFLOW_DIR = "file:///mlruns"  # save experiments as files (relative path)
MLFLOW_DIR = "sqlite:///mlruns.db"  # save experiments in a sqlite db (relative path)


# --- Pipeline steps ---

@dpipe.delayed_cached()
def load_data_1():
    sleep(1)
    return pd.DataFrame({'a': [1., 2., 3., 5., 6.]})


@dpipe.delayed_cached()
def load_data_2():
    sleep(1)
    return pd.DataFrame({'b': [1., 1., 1., 1., 0.], 'c': ['us', 'us', 'au', 'us', 'au']})


@dpipe.delayed_cached()
def load_data_3():
    sleep(1)
    return pd.DataFrame({'d': [-1., -1., np.nan, -3., -1.], 'e': [0, 1, -2., 0, 0]})


@dpipe.delayed_cached(name_prefix=PREFIX, nout=2)
def make_x_y(df_1, df_2, df_3, include_country, adjust_for_country, target, fversion):
    assert fversion is not None
    sleep(1)
    df = pd.concat((df_1, df_2, df_3), axis=1)
    if adjust_for_country:
        df['b'] = df['b'] + 2 * (df['c'] == 'au')
    if not include_country:
        df = df.drop(columns=['c'])
    else:
        df['c'] = df['c'].map({'us': 0, 'eu': 1, 'au': 2})
    y = df[target]
    X = df.drop(columns=[target])
    return X, y


@dpipe.delayed_cached(name_prefix=PREFIX, nout=4)
def split_x_y(X, y, test_ratio):
    assert len(X) == len(y)
    assert 0 < test_ratio < 1.
    n_test = int(len(X) * test_ratio)
    return X[:-n_test], X[-n_test:], y[:-n_test], y[-n_test:]


@dpipe.delayed_cached(name_prefix=PREFIX, nout=2)
def crossval_model(model_name, _model, X, y, n_folds, mversion, n_jobs=1):
    assert model_name is not None
    assert mversion is not None
    cv = KFold(n_folds)
    scores = {
        'mae': make_scorer(mean_absolute_error, greater_is_better=False),
        'r2': make_scorer(r2_score),
    }
    results = cross_validate(
        _model, X, y,
        scoring=scores,
        cv=cv,
        return_train_score=True,
        n_jobs=n_jobs,
    )
    _model.fit(X, y)

    mlflow.set_tracking_uri(MLFLOW_DIR)
    mlflow.set_experiment(PREFIX)
    with mlflow.start_run():
        mlflow.log_params(params.get_params())
        metrics = {}
        for k, v in results.items():
            if k.startswith('train_') or k.startswith('test_'):
                metrics[k] = v.mean()
        mlflow.log_metrics(metrics)
    
    return _model, results


# --- Pipeline parameters ---

params = dpipe.DelayedParameters()
params.create_many(dict(
    fversion=None,
    mversion=None,
    include_country=None,
    adjust_for_country=None,
    target=None,
    test_ratio=None,
    n_folds=None,
    model_name=None,
    _model=None,
    _n_jobs=1,
))


# --- Pipeline ---

data_1 = load_data_1()
data_2 = load_data_2()
data_3 = load_data_3()
X, y = make_x_y(
    df_1=data_1,
    df_2=data_2,
    df_3=data_3,
    include_country=params.get_delayed('include_country'),
    adjust_for_country=params.get_delayed('adjust_for_country'),
    target=params.get_delayed('target'),
    fversion=params.get_delayed('fversion'),
)
X_train, X_test, y_train, y_test = split_x_y(
    X=X,
    y=y,
    test_ratio=params.get_delayed('test_ratio'),
)
cv_model, cv_results = crossval_model(
    model_name=params.get_delayed('model_name'),
    _model=params.get_delayed('_model'),
    X=X_train,
    y=y_train,
    n_folds=params.get_delayed('n_folds'),
    mversion=params.get_delayed('mversion'),
    n_jobs=params.get_delayed('_n_jobs'),
)


def run_experiment(save_model_mlflow_dir=None):
    """Run experiment pipeline
    
    Configure pipeline parameters via dpipe.delayed_context
    """
    cv_model_, cv_results_ = dpipe.delayed_compute((cv_model, cv_results))
    if save_model_mlflow_dir is not None:
        mlflow.sklearn.save_model(cv_model_, Path('model') / save_model_mlflow_dir)
    logger.info('Experiment run is finished')
    return cv_model_, cv_results_
