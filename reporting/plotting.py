def plot_study_data(labels, subjects, series, mode="all"):
    # Matplotlib is imported only when the user explicitly requests a plot.
    import matplotlib.pyplot as plt

    if mode in {"total", "all"}:
        values = [sum(series[name][i] for name in subjects) for i in range(len(labels))]
        plt.plot(labels, [v / 60 for v in values], marker="o", label="Total study time")
    elif mode == "one":
        if not subjects:
            print("No data found for that subject.")
            return
        name = subjects[0]
        plt.plot(labels, [v / 60 for v in series[name]], marker="o", label=name)

    plt.xlabel("Date / period")
    plt.ylabel("Study time (hours)")
    plt.title("Study time")
    plt.xticks(rotation=45, ha="right")
    if subjects or mode in {"total", "all"}:
        plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
