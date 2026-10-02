import matplotlib.pyplot as plt
from analyze import load_data

def plot_indicators(df):
    # criar uma figura com 4 subplots (grade 2x2), um por indicador
    # dica: fig, axed = plt.subplots(2, 2, figsize=(12,8))
    fig, axes = plt.subplots(2, 2, figsize=(12,8))

    # para cada coluna do df, plotar a serie no eixo correspondente
    # dica: zip(df.columns, axes, flatten()) deixa interar as 4 colunas junto com os 4 eixos
    for column, ax in zip(df.columns, axes.flatten()):
        ax.plot(df[column], label=column, color='blue')
        ax.set_title(column)

    plt.tight_layout()
    plt.savefig("data/processed/indicators_overview.png")
    plt.show() 



if __name__ == "__main__":
    df = load_data()
    plot_indicators(df)
