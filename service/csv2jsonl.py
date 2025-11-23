import json

import pandas as pd


class CsvToJsonlConverter:
    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file

    def convert(self):
        df = pd.read_csv(self.input_file, quotechar='"')

        # df["entities"] = df["entities"].apply(lambda x: [e.strip() for e in x.split(",")])
        # df["keywords"] = df["keywords"].apply(lambda x: [k.strip() for k in x.split(",")])
        df["entities"] = df["entities"].apply(
            lambda x: [e.strip() for e in str(x).split(",")] if pd.notna(x) else []
        )
        df["keywords"] = df["keywords"].apply(
            lambda x: [k.strip() for k in str(x).split(",")] if pd.notna(x) else []
        )

        with open(self.output_file, "w", encoding="utf-8", newline="") as f:
            for _, row in df.iterrows():
                json.dump({
                    "summary": row["summary"],
                    "entities": row["entities"],
                    "keywords": row["keywords"]
                }, f)
                f.write("\n")
