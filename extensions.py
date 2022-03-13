from distutils import extension
import pandas as pd

def filter_extensions(csv, extensions):
    df = pd.read_csv(csv)
    df["extension"] = df["image_url"].apply(lambda x: x.split(".")[-1].split("?")[0].lower())

    print("Extensions found:")
    print(set(df["extension"].to_list()))

    print("Removing files with unsupported extensions:")
    print(df[~df["extension"].isin(extensions)]["image_url"])

    df = df[df["extension"].isin(extensions)]
    df.to_csv(csv, index=False)

if __name__ == "__main__":
    print("USAGE: combine(inputfiles, outputfolder)")
