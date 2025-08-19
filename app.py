from flask import Flask, render_template, request, jsonify
import math
import re
#http://127.0.0.1:5000 to search fro the app 
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def _preprocess_expression(expression: str) -> str:
    # Replace common calculator syntax with Python equivalents
    expr = expression
    expr = expr.replace('^', '**')
    # Support ln() as natural log
    expr = re.sub(r'\bln\s*\(', 'log(', expr)
    # Replace factorial for simple numeric operands: 5! -> factorial(5)
    expr = re.sub(r'(?P<num>(?:\d+\.?\d*))\s*!', r'factorial(\g<num>)', expr)
    return expr

def _safe_eval(expression: str):
    # Allowed math functions and constants
    allowed_names = {
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'sqrt': math.sqrt,
        'log': math.log,      # natural log (used via ln->log replacement)
        'log10': math.log10,  # base-10 log (use as log10())
        'exp': math.exp,
        'pow': pow,
        'abs': abs,
        'round': round,
        'pi': math.pi,
        'e': math.e,
        'factorial': math.factorial,
    }
    expr = _preprocess_expression(expression)
    return eval(expr, {'__builtins__': {}}, allowed_names)

@app.route('/calc', methods=['POST'])
def calc():
    data = request.get_json(force=True)
    expression = data.get('expression', '')
    try:
        result = _safe_eval(expression)
        # Convert result to a regular float or int where reasonable
        if isinstance(result, float):
            # Limit very long floats
            result = float(f"{result:.12g}")
        return jsonify({'ok': True, 'result': result})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400

# ---- Converters ----

_length_to_m = {
    'm': 1.0,
    'km': 1000.0,
    'cm': 0.01,
    'mm': 0.001,
    'in': 0.0254,
    'ft': 0.3048,
    'yd': 0.9144,
    'mi': 1609.344,
}

_mass_to_kg = {
    'kg': 1.0,
    'g': 0.001,
    'mg': 1e-6,
    'lb': 0.45359237,
    'oz': 0.028349523125,
    't': 1000.0,  # metric ton
}

_volume_to_l = {
    'L': 1.0,
    'mL': 0.001,
    'gal': 3.785411784,  # US gallon
    'qt': 0.946352946,   # US quart
    'pt': 0.473176473,   # US pint
    'cup': 0.2365882365, # US cup
    'tbsp': 0.0147867648,
    'tsp': 0.00492892159,
}

def _convert_temperature(value: float, from_u: str, to_u: str) -> float:
    f = from_u.lower()
    t = to_u.lower()
    if f == t:
        return value
    # Convert to Celsius first
    if f == 'c':
        c = value
    elif f == 'f':
        c = (value - 32.0) * (5.0/9.0)
    elif f == 'k':
        c = value - 273.15
    else:
        raise ValueError('Unsupported temperature unit')
    # Celsius to target
    if t == 'c':
        return c
    if t == 'f':
        return (c * 9.0/5.0) + 32.0
    if t == 'k':
        return c + 273.15
    raise ValueError('Unsupported temperature unit')

@app.route('/convert/unit', methods=['POST'])
def convert_unit():
    data = request.get_json(force=True)
    category = data.get('category')
    from_unit = data.get('from')
    to_unit = data.get('to')
    value = float(data.get('value', 0))
    try:
        if category == 'length':
            meters = value * _length_to_m[from_unit]
            result = meters / _length_to_m[to_unit]
        elif category == 'mass':
            kg = value * _mass_to_kg[from_unit]
            result = kg / _mass_to_kg[to_unit]
        elif category == 'volume':
            liters = value * _volume_to_l[from_unit]
            result = liters / _volume_to_l[to_unit]
        elif category == 'temperature':
            result = _convert_temperature(value, from_unit, to_unit)
        else:
            return jsonify({'ok': False, 'error': 'Unsupported category'}), 400
        return jsonify({'ok': True, 'result': result})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400

# Static currency rates relative to USD (example rates; not real-time)
_currency_to_usd = {
    'USD': 1.0,
    'EUR': 1.09,
    'GBP': 1.28,
    'JPY': 0.0065,
    'INR': 0.012,
    'PKR': 0.0036,
    'CNY': 0.14,
    'AUD': 0.67,
    'CAD': 0.73,
}

@app.route('/convert/currency', methods=['POST'])
def convert_currency():
    data = request.get_json(force=True)
    from_ccy = data.get('from')
    to_ccy = data.get('to')
    value = float(data.get('value', 0))
    try:
        usd = value * _currency_to_usd[from_ccy]
        result = usd / _currency_to_usd[to_ccy]
        return jsonify({'ok': True, 'result': result})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400

_datasize_si = {
    'B': 1.0,
    'KB': 1000.0,
    'MB': 1000.0**2,
    'GB': 1000.0**3,
    'TB': 1000.0**4,
}

_datasize_iec = {
    'B': 1.0,
    'KiB': 1024.0,
    'MiB': 1024.0**2,
    'GiB': 1024.0**3,
    'TiB': 1024.0**4,
}

@app.route('/convert/datasize', methods=['POST'])
def convert_datasize():
    data = request.get_json(force=True)
    from_u = data.get('from')
    to_u = data.get('to')
    value = float(data.get('value', 0))
    try:
        tables = [{**_datasize_si}, {**_datasize_iec}]
        # Determine which table contains both units
        table = None
        for t in tables:
            if from_u in t and to_u in t:
                table = t
                break
        if table is None:
            # Allow cross SI/IEC conversions by converting through bytes
            factor_from = _datasize_si.get(from_u, _datasize_iec.get(from_u))
            factor_to = _datasize_si.get(to_u, _datasize_iec.get(to_u))
        else:
            factor_from = table[from_u]
            factor_to = table[to_u]
        result = value * factor_from / factor_to
        return jsonify({'ok': True, 'result': result})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400

if __name__ == '__main__':
    app.run(debug=True) 