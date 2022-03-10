import os
import zipfile

def unzip(folder, target):
    for root, dir, files in os.walk(folder):
        for file in files:
            if ".zip" not in file:
                continue

            target = os.path.join(target, file.replace(".zip",""))
            print(target)

            if not os.path.exists(target):
                os.makedirs(target)

            with zipfile.ZipFile(os.path.join(folder, file), 'r') as zip_ref:
                zip_ref.extractall(target)


if __name__ == "__main__":
    print("USAGE: unzip(folder)")
