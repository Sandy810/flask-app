from flask import Flask, render_template, request
from rapidfuzz import fuzz
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
    previous_row = None  # 記錄前一行，處理欄位不完整的情況
    try:
        with pdfplumber.open(pdf_file_name) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()  # 提取所有表格
                for table in tables:
                    for row in table:
                        # 清理每個儲存格的內容，去除換行符和首尾空格
                        row = [cell.replace("\n", "").strip() if isinstance(cell, str) else cell for cell in row]
                        
                        # 若當前行缺少欄位，補全缺失的部分
                        if row:
                            if previous_row and len(row) < len(previous_row):
                                for i in range(len(row), len(previous_row)):
                                    row.append(previous_row[i])
                            data.append(row)
                            previous_row = row  # 更新 previous_row
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
    results = []  # 存放搜尋結果
    for row in data:
        if len(row) >= 4 and row[2]:  # 確保該行至少有四個欄位且“細項說明”欄位不為 None
            detail_column = row[2]  # 假設細項說明在第三個欄位，即索引為 2
            similarity = fuzz.partial_ratio(keyword, detail_column)  # 計算相似度
            if similarity >= 70:  # 提高相似度閾值，降低誤匹配
                results.append(row)  # 如果匹配，將該行加入結果
    return results


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # 使用 Render 提供的 PORT 環境變數
    app.run(host='0.0.0.0', port=port)
