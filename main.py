from flask import Flask, request, jsonify, render_template
import csv
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
DATA_DIR = "data"  # 資料存放目錄

# 主頁路由 (渲染表單頁面)
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# 新增記錄的路由
@app.route("/add", methods=["POST"])
def add_record():
    shop = request.form.get('shop', '未指定店鋪')
    machine = request.form.get('machine', '未指定機台')
    amount = request.form.get('amount', '0')
    date = request.form.get('date') or datetime.now().strftime("%Y-%m-%d")
    month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y_%m")
    file_path = os.path.join(DATA_DIR, f"{month}.csv")

    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        with open(file_path, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([date, shop, machine, amount])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# 讀取記錄的路由 (顯示儲存的數據)
@app.route("/read", methods=["GET"])
def read_records():
    records_by_month = defaultdict(lambda: defaultdict(list))
    totals_by_month = defaultdict(lambda: defaultdict(int))

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # 讀取所有月份的檔案
    for file_name in os.listdir(DATA_DIR):
        if file_name.endswith(".csv"):
            month = file_name.split(".")[0]
            file_path = os.path.join(DATA_DIR, file_name)
            with open(file_path, "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    date, shop, machine, amount = row
                    records_by_month[month][shop].append((date, machine, int(amount)))
                    totals_by_month[month][shop] += int(amount)

    return render_template("read.html", records_by_month=records_by_month, totals_by_month=totals_by_month)

# 刪除記錄的路由
@app.route("/delete", methods=["POST"])
def delete_record():
    month = request.form.get("month")
    shop = request.form.get("shop")
    index = int(request.form.get("index"))
    file_path = os.path.join(DATA_DIR, f"{month}.csv")

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "檔案不存在"})

    try:
        with open(file_path, "r") as csvfile:
            records = list(csv.reader(csvfile))

        # 過濾掉需要刪除的記錄
        filtered_records = [record for i, record in enumerate(records) if not (record[1] == shop and i == index)]

        # 寫回檔案
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(filtered_records)

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# 404 錯誤處理
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "請求的 URL 在伺服器上不存在", "url": request.path}), 404

if __name__ == "__main__":
    app.run(debug=True)

