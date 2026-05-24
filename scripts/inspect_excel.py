import pandas as pd

def inspect_excel():
    excel_path = "c:\\Users\\tsuma.thomas\\Documents\\Sunculture\\data\\raw\\Senior_Data_Scientist_Assessment_Data (1) (1) (1) (1).xlsx"
    xl = pd.ExcelFile(excel_path)
    print("Sheets in Excel file:")
    for sheet in xl.sheet_names:
        print(f" - {sheet}")
        
    print("\n--- Columns and Sample Rows for each sheet ---")
    for sheet in xl.sheet_names:
        df = xl.parse(sheet, nrows=3)
        print(f"\nSheet: {sheet} (shape preview: {df.shape})")
        print("Columns:", list(df.columns))
        print(df.head(2))

if __name__ == "__main__":
    inspect_excel()
