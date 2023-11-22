import sys
import re
import pandas as pd


def read_chat(chat_file: str) -> str:
    """Reads a WhatsApp chat file and returns it as a string."""
    with open(chat_file, "r", encoding="utf-8") as f:
        chat = f.read()
    return chat


def parse_chat(chat: str) -> list[tuple[str, str]]:
    """Splits a WhatsApp chat string into a list of messages."""
    pattern = r"(\b\d{1,2}/\d{1,2}/\d{2}, \d{2}:\d{2}\b)\s-\s"
    split = re.split(pattern, chat, flags=re.MULTILINE)
    split = [line.strip() for line in split if line.strip()]  # remove any empty strings

    messages = list(zip(split[::2], split[1::2]))
    messages = [[m[0]] + m[1].split(":", maxsplit=1) for m in messages if ":" in m[1]]

    return messages


def parse_messages(messages: list[tuple[str, str]]) -> pd.DataFrame:
    """Parses a list of messages into a pandas DataFrame."""
    df = pd.DataFrame(messages, columns=["date", "sender", "message"])
    df.index = pd.to_datetime(df["date"], format="%m/%d/%y, %H:%M")
    df["day_of_week"] = df.index.day_of_week
    df["day_name"] = df.index.day_name()
    df["time"] = pd.to_datetime(df.index.time, format="%H:%M:%S")
    df.drop(columns=["date"], inplace=True)

    df = df[df["message"].str.contains(r"\d+[\.,]?\d*")]
    df["number"] = (
        df["message"]
        .str.extract(r"(\d+[\.,]?\d*)", expand=False)
        .str.replace(",", ".")
        .astype(float)
    )
    df = df.sort_values(by=["day_of_week", "time"])
    df = df[df.number < 7]

    return df


def plot_data(df: pd.DataFrame):
    """Plots the data using Plotly."""
    fig = df.plot.line(
        backend="plotly",
        x="time",
        y="number",
        color="day_name",
        markers=True,
        labels={"day_name": "Dia", "number": "Fila"},
        title="Fila Cantina",
        height=600,
    )
    fig.update_layout(xaxis={"title": "Time"}, yaxis={"title": "Fila"})
    fig.update_layout(legend={"title": "Dia"})
    fig.write_html("fila.html")


def main(chat_file: str):
    chat = read_chat(chat_file)
    messages = parse_chat(chat)[5:]
    df = parse_messages(messages)

    plot_data(df)


if __name__ == "__main__":
    main(sys.argv[1])
