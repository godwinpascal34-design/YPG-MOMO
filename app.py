import gspread
from flask import Flask, request, jsonify

app = Flask(__name__)

# Authenticate with Google Sheets
# Ensure credentials.json is in your GitHub repo folder
gc = gspread.service_account(filename='credentials.json')

# Open your spreadsheet
sh = gc.open("Ajikpo YPG MOMO") 
worksheet = sh.sheet1

@app.route('/momo-webhook', methods=['POST'])
def momo_webhook():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data"}), 400

    # Extracting data safely
    tx_id = data.get('financialTransactionId', 'N/A')
    amount = float(data.get('amount', 0))
    tx_type = data.get('transactionType', 'N/A')
    party = data.get('payerOrReceiver', 'N/A')
    timestamp = data.get('timestamp', 'N/A')
    reference = data.get('reference', 'N/A')

    # Formatting logic
    final_amount = amount if tx_type in ["DEPOSIT", "RECEIVE"] else -amount
    display_type = "Received" if tx_type in ["DEPOSIT", "RECEIVE"] else tx_type.capitalize()

    # Append to Google Sheet
    try:
        worksheet.append_row([timestamp, tx_id, display_type, final_amount, party, reference])
        return jsonify({"status": "SUCCESS"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()