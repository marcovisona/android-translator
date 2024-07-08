import pandas as pd


def convert_to_excel(csv_file):
    excel_file = csv_file.with_suffix('.xlsx')
    try:
        print(f"Converting {csv_file} to {excel_file}")
        df = pd.read_csv(csv_file)

        df.to_excel(excel_file, index=False)
    except Exception as e:
        print(f"Ignored file")
