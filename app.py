import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Paste your free Power Automate Webhook URL here once you generate it
POWER_AUTOMATE_URL = os.environ.get("POWER_AUTOMATE_URL", "YOUR_POWER_AUTOMATE_URL_HERE")

@app.route('/momo-webhook', methods=['POST'])
def momo_webhook():
    # 1. Capture the raw transaction data sent from the mobile money network
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    tx_type = data.get('transactionType')  # DEPOSIT, SEND, WITHDRAWAL
    tx_id = data.get('financialTransactionId')
    amount = float(data.get('amount', 0))
    party = data.get('payerOrReceiver')
    fee = data.get('fee', 0.0)
    timestamp = data.get('timestamp')
    # ADDED HERE: Extracting the reference/description from the MoMo data
    reference = data.get('reference', 'N/A') 

    # 2. Adjust format dynamically based on cash flow direction
    if tx_type in ["DEPOSIT", "RECEIVE"]:
        display_type = "Received"
        final_amount = amount
    elif tx_type in ["SEND", "WITHDRAWAL"]:
        display_type = tx_type.capitalize()
        final_amount = -amount
    else:
        display_type = "Other"
        final_amount = amount

    # 3. Forward this clean data right to your Excel destination via Power Automate
    excel_payload = {
        "timestamp": timestamp,
        "transactionId": tx_id,
        "type": display_type,
        "amount": final_amount,
        "fee": fee,
        "party": party,
        "reference": reference  # ADDED HERE: Included in the bundle sent to Excel
    }

    print(f"Forwarding {display_type}: {final_amount} GHS (Ref: {reference}) for ID {tx_id}")

    # Fire the data across the web straight into Microsoft's ecosystem
    if "YOUR_POWER_AUTOMATE_URL_HERE" not in POWER_AUTOMATE_URL:
        try:
            response = requests.post(POWER_AUTOMATE_URL, json=excel_payload, timeout=10)
            print(f"Excel Sync Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to sync with Excel: {e}")
    else:
        print("Excel Sync skipped: Power Automate URL not set up yet.")
    
    # Return success response back to telecom network
    return jsonify({"status": "SUCCESS"}), 200

if __name__ == '__main__':
    # Run server locally if testing
    app.run(port=5000)