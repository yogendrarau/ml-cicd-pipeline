from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

def load_splits(random_seed=42, test_size=0.2, stratify=True):
    data = load_iris()
    X, y = data.data, data.target
    strat = y if stratify else None
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=test_size, stratify=strat, random_state=random_seed
    )
    return (X_tr, y_tr), (X_te, y_te), data