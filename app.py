from flask import Flask, render_template, request, jsonify, redirect, url_for
import database

app = Flask("Smart")

database.init_db()

@app.route('/')
def index():
    sync_msg = database.sync_to_neon()
    sales = database.get_all_sales()
    return render_template('index.html', sales=sales, sync_message=sync_msg)

#Submission post router
@app.route('/api/add_sale', methods=['POST'])
def add_sale_api():
    laptop_model = request.form.get('laptop_model')
    price = request.form.get('price')
    quantity = request.form.get('quantity')

    if not laptop_model or not price or not quantity:
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

    try:
        # 1. Insert into local SQLite and get created dict
        sale_record = database.add_sale(laptop_model, float(price), int(quantity))

        # 2. Attempt push to Neon Cloud
        sync_msg = database.sync_to_neon()

        # 3. Check synced flag status
        unsynced_ids = [s['id'] for s in database.get_unsynced_sales()]
        if sale_record['id'] not in unsynced_ids:
            sale_record['is_synced'] = 1

        return jsonify({
            'status': 'success',
            'message': sync_msg,
            'sale': sale_record
        })

    except Exception as e:
        print(f"[ERROR in /api/add_sale]: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sync', methods=['POST'])
def trigger_sync_api():
    sync_msg = database.sync_to_neon()
    sales = [dict(s) for s in database.get_all_sales()]
    return jsonify({
        'status': 'success',
        'message': sync_msg,
        'sales': sales
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)