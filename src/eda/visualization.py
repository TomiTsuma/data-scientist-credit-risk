import matplotlib.pyplot as plt
import seaborn as sns


def plot_distribution(series, title: str):
    plt.figure(figsize=(8, 4))
    sns.histplot(series.dropna(), kde=True)
    plt.title(title)
    plt.tight_layout()
    return plt
