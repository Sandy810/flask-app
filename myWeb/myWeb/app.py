from flask import Flask, render_template, request
import requests
import pdfplumber
import os

app = Flask(__name__)

# 目標 PDF 文件的 URL
url = 'https://www-ws.pthg.gov.tw/Upload/2015pthg/62/relfile/9295/391180/5cff5a41-36f9-40e8-8243-a030e2e2138d.pdf'
pdf_file_name = 'temp_downloaded.pdf'

def download_pdf():
    # 檢查是否已存在 temp_downloaded.pdf，若存在則刪除
    if os.path.exists(pdf_file_name):
        os.remove(pdf_file_name)

    # 嘗試下載 PDF 文件
    try:
        response = requests.get(url)
        response.raise_for_status()

        # 將下載的 PDF 文件保存到本地
        with open(pdf_file_name, 'wb') as f:
            f.write(response.content)

        print(f'PDF 文件 "{pdf_file_name}" 下載成功！')

    except requests.exceptions.RequestException as e:
        print(f"下載 PDF 時出錯: {e}")

def extract_table_from_pdf(pdf_file_name):
    data = []  # 存放處理後的表格數據
    previous_row = None  # 初始化 previous_row 為 None，避免未賦值錯誤
    try:
        with pdfplumber.open(pdf_file_name) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()  # 提取所有表格
                for table in tables:
                    for row in table:
                        # 檢查是否存在換行符 \n 並合併
                        row = [cell.replace("\n", " ") if isinstance(cell, str) else cell for cell in row]
                        
                        # 檢查行是否缺少欄位(可能因合併欄位導致)
                        if row:
                            if previous_row and len(row) < len(previous_row):
                                # 合併欄位情況，補全缺失欄位
                                for i in range(len(row), len(previous_row)):
                                    row.append(previous_row[i])

                            # 處理補全後的行
                            data.append(row)
                            # 更新 previous_row 以便處理下一行
                            previous_row = row
                        else:
                            print(f"跳過空行: {row}")
        return data
    except Exception as e:
        print(f"提取過程中出現錯誤: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        item = request.form['item']
        download_pdf()  # 下載 PDF 文件
        data = extract_table_from_pdf(pdf_file_name)  # 提取表格數據

        if data:
            results = query_by_keyword(item, data)

    return render_template('index.html', results=results)

def query_by_keyword(keyword, data):
    results = [row for row in data if keyword in row[2]]
    return results

if __name__ == '__main__':
    app.run(debug=True)