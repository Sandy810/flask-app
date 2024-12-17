from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

def classify_garbage(user_input):
    garbage_categories = {
        "recyclable": ["paper", "plastic bottle", "metal can", "glass"],
        "hazardous": ["battery", "paint", "medicine", "light bulb"],
        "kitchen waste": ["fruit peel", "vegetable", "leftovers", "coffee grounds"],
        "general waste": ["cigarette butt", "dust", "tissue", "diaper"]
    }

    handling_methods = {
        "recyclable": "這是可回收物品。請清理後放入可回收垃圾桶。",
        "hazardous": "這是有害垃圾。請將其送到指定的回收點處理。",
        "kitchen waste": "這是廚餘垃圾。請放入廚餘垃圾桶處理。",
        "general waste": "這是一般垃圾。請放入一般垃圾桶處理。"
    }

    normalized_input = user_input.lower()

    for category, keywords in garbage_categories.items():
        for keyword in keywords:
            if re.search(rf"\b{keyword}\b", normalized_input):
                return f"分類: {category.capitalize()}\n{handling_methods[category]}"
    
    return "無法分類輸入內容。請提供更多細節或檢查描述。"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    user_input = request.form['user_input']
    result = classify_garbage(user_input)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)