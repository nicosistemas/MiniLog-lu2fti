from flask import Flask, render_template, request, redirect, send_file
import csv
import os
from datetime import datetime, timezone
from flask import jsonify

app = Flask(__name__)

# ================================
# Archivos (dentro del contenedor)
# ================================
CONTACTS_FILE = "contacts.csv"
OPERATOR_FILE = "operator_id.txt"

last_mode = ''
last_frequency = ''

# ================================
# Operador
# ================================
def save_operator_id(op_id):
    with open(OPERATOR_FILE, 'w') as f:
        f.write(op_id)

def load_operator_id():
    if os.path.exists(OPERATOR_FILE):
        with open(OPERATOR_FILE, 'r') as f:
            return f.read().strip()
    return 'LU2FTI'

operator_id = load_operator_id()

# ================================
# Helpers
# ================================
def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return []
    with open(CONTACTS_FILE, newline='') as f:
        return list(csv.reader(f))

def save_contacts(contacts):
    with open(CONTACTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(contacts)

def get_band(frequency):
    try:
        frequency = float(frequency)
    except ValueError:
        return "UNKNOWN"

    if 1.8 <= frequency < 2.0:
        return "160m"
    elif 3.5 <= frequency < 4.0:
        return "80m"
    elif 5.0 <= frequency < 5.5:
        return "60m"
    elif 7.0 <= frequency < 7.3:
        return "40m"
    elif 10.1 <= frequency < 10.15:
        return "30m"
    elif 14.0 <= frequency < 14.35:
        return "20m"
    elif 18.068 <= frequency < 18.168:
        return "17m"
    elif 21.0 <= frequency < 21.45:
        return "15m"
    elif 24.89 <= frequency < 24.99:
        return "12m"
    elif 28.0 <= frequency < 29.7:
        return "10m"
    elif 50.0 <= frequency < 54.0:
        return "6m"
    elif 144.0 <= frequency < 148.0:
        return "2m"
    elif 430.0 <= frequency < 450.0:
        return "70cm"
    return "UNKNOWN"

# ================================
# DXCC (cty.dat)
# ================================
def load_cty():
    prefixes = {}
    exact_calls = {}
    current_country = None

    with open("cty.dat", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if ":" in line:
                parts = line.split(":")
                current_country = parts[0].strip()
                continue

            if not current_country:
                continue

            line = line.replace(";", "")
            items = line.split(",")

            for item in items:
                item = item.strip().upper()

                if not item:
                    continue

                is_exact = item.startswith("=")

                item = item.replace("=", "")
                item = item.split("(")[0]
                item = item.split("[")[0]
                item = item.strip()

                if not item:
                    continue

                if is_exact:
                    exact_calls[item] = current_country
                else:
                    prefixes[item] = current_country

    prefixes = dict(sorted(prefixes.items(), key=lambda x: -len(x[0])))

    return prefixes, exact_calls


def get_country(call, prefixes, exact_calls):
    call = call.upper()

    if call in exact_calls:
        return exact_calls[call]

    for prefix in prefixes:
        if call.startswith(prefix):
            return prefixes[prefix]

    return "UNKNOWN"

PREFIXES, EXACT_CALLS = load_cty()

# ================================
# Routes
# ================================
@app.route('/', methods=['GET', 'POST'])
def index():
    global last_mode, last_frequency, operator_id

    if request.method == 'POST':
        if 'operator_id' in request.form and request.form['operator_id']:
            operator_id = request.form['operator_id']
            save_operator_id(operator_id)

        contact_id = request.form['id'].upper()
        mode = request.form['mode']
        try:
            frequency = float(request.form['frequency'].replace(',', '.'))
            frequency = f"{frequency:.3f}"
        except ValueError:
            return redirect('/')
        ##frequency = request.form['frequency']
        extra = request.form['extra']
        date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        last_mode = mode
        last_frequency = frequency

        contacts = load_contacts()
        contacts.append([date, contact_id, mode, frequency, extra, operator_id])
        save_contacts(contacts)

        return redirect('/')

    contacts = load_contacts()
    contacts_with_index = list(enumerate(contacts))[::-1]

    return render_template(
        'index.html',
        contacts=contacts_with_index,
        last_mode=last_mode,
        last_frequency=last_frequency,
        operator_id=operator_id
    )

# ================================
# Editar
# ================================
@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    contacts = load_contacts()

    if index >= len(contacts):
        return "Contacto no encontrado", 404

    if request.method == 'POST':
        contacts[index][1] = request.form['id'].upper()
        ##contacts[index][1] = request.form['id']
        contacts[index][2] = request.form['mode']
        ##contacts[index][3] = request.form['frequency']
        try:
          freq = float(request.form['frequency'].replace(',', '.'))
          contacts[index][3] = f"{freq:.3f}"
        except ValueError:
          return redirect('/')
        contacts[index][4] = request.form['extra']

        save_contacts(contacts)
        return redirect('/')

    return render_template('edit.html', contact=contacts[index], index=index)

# ================================
# Eliminar
# ================================
@app.route('/delete/<int:index>')
def delete(index):
    contacts = load_contacts()

    if index >= len(contacts):
        return "Contacto no encontrado", 404

    contacts.pop(index)
    save_contacts(contacts)

    return redirect('/')

# ================================
# Exportar ADIF
# ================================
@app.route('/export')
def export():
    contacts = load_contacts()

    if not operator_id:
        op_id = 'UNKNOWN'
    else:
        op_id = operator_id

    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"contacts-{current_time}.adi"

    adi_content = "Generated by MiniLog by LU2FTI\n"

    for c in contacts:
        if len(c) < 6:
            continue

        band = get_band(c[3])
        extra = c[4] if len(c) > 4 else ''
        qso_date = c[0].split()[0].replace("-", "")

        try:
            time_on = datetime.strptime(c[0], '%Y-%m-%d %H:%M:%S').strftime('%H%M%S')
        except ValueError:
            time_on = '000000'

        adi_content += f"<station_callsign:{len(op_id)}>{op_id} "
        adi_content += f"<call:{len(c[1])}>{c[1]} "
        adi_content += f"<qso_date:{len(qso_date)}>{qso_date} "
        adi_content += f"<time_on:{len(time_on)}>{time_on} "
        adi_content += f"<band:{len(band)}>{band} "
        adi_content += f"<freq:{len(c[3])}>{c[3]} "
        adi_content += f"<mode:{len(c[2])}>{c[2]} "
        adi_content += f"<extra:{len(extra)}>{extra} <eor>\n"

    if adi_content.strip() == "Generated by MiniLog by LU2FTI":
        return "No hay contactos para exportar"

    with open(filename, 'w') as f:
        f.write(adi_content)

    return send_file(filename, as_attachment=True)

# ================================
# buscador de Country
# ================================

@app.route('/lookup')
def lookup():
    call = request.args.get('call', '').upper()

    if not call:
        return {"country": ""}

    country = get_country(call, PREFIXES, EXACT_CALLS)

    return {"country": country}

# ================================
# Endpoint API QSO
# ================================

@app.route("/api/qso", methods=["POST"])
def api_qso():
    data = request.get_json()

    if not data:
        return jsonify({"error": "no data"}), 400

    call = data.get("call", "").strip().upper()
    mode = data.get("mode", "")
    freq = data.get("freq", 0)
    mycall = data.get("mycall", "")
    timestamp = data.get("timestamp")

    if not call:
        return jsonify({"error": "missing call"}), 400

    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    contacts = load_contacts()
    contacts.append([
        timestamp,
        call,
        mode,
        str(freq),
        data.get("extra", ""),
        mycall
    ])

    save_contacts(contacts)

    return jsonify({
        "status": "ok",
        "call": call,
        "mode": mode
    })

# ================================
# Run
# ================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
