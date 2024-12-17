from flask import render_template

def hello_world():
    return "Hello, MVC框架!"

def index():
    title ="智能垃圾分類系統"
    big_word ="歡迎使用智能垃圾分類系統！"
    return render_template('index.html',title=title,big_word=big_word) 