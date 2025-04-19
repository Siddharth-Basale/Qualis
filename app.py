from flask import Flask, render_template, request, redirect, url_for, make_response, session
from werkzeug.utils import secure_filename
import os
import pdfkit

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16 MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['SECRET_KEY'] = 'your_secret_key'

# Configure path to wkhtmltopdf binary
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=r'wkhtmltopdf\bin\wkhtmltopdf.exe')  # Update this path as needed

# PDFKit options
PDFKIT_OPTIONS = {
    'enable-local-file-access': '',
    'quiet': '',
    'margin-top': '10mm',
    'margin-right': '10mm',
    'margin-bottom': '10mm',
    'margin-left': '10mm'
}

@app.route('/', methods=['GET', 'POST'])
def pcp_type_selection():
    if request.method == 'POST':
        pcp_type = request.form['pcp_type']
        session['pcp_type'] = pcp_type
        return redirect(url_for('customer_details', pcp_type=pcp_type))
    return render_template('pcp_type_selection.html')

@app.route('/customer_details', methods=['GET', 'POST'])
def customer_details():
    pcp_type = request.args.get('pcp_type', session.get('pcp_type', ''))
    if request.method == 'POST':
        session['customer_name'] = request.form['customer_name']
        session['short_name'] = request.form['short_name']
        session['type_value'] = request.form['type']
        return redirect(url_for('introduction'))
    return render_template('customer_details.html', pcp_type=pcp_type)

@app.route('/introduction')
def introduction():
    customer_name = request.args.get('customer_name', session.get('customer_name', ''))
    short_name = request.args.get('short_name', session.get('short_name', ''))
    type_value = request.args.get('type_value', session.get('type_value', ''))
    pcp_type = request.args.get('pcp_type', session.get('pcp_type', ''))
    return render_template('introduction.html', 
                         customer_name=customer_name, 
                         short_name=short_name, 
                         type_value=type_value, 
                         pcp_type=pcp_type)

@app.route('/physical_layer_1', methods=['POST'])
def physical_layer_1():
    pcp_type = request.args.get('pcp_type', session.get('pcp_type', 'PCP-A'))
    customer_name = request.args.get('customer_name', session.get('customer_name', ''))

    image_map = {
        'PCP-A': 'pcp_a_diagram.png',
        'PCP-B': 'pcp_b_diagram.png',
        'PCP-C': 'pcp_c_diagram.png',
        'PCP-D': 'pcp_d_diagram.png',
    }

    network_diagram = image_map.get(pcp_type, 'default_diagram.png')

    return render_template(
        'physical_layer_1.html',
        pcp_type=pcp_type,
        customer_name=customer_name,
        network_diagram=network_diagram,
        logo_path=None,
        network_diagram_path=None,
        css_path=url_for('static', filename='styles.css')
    )

@app.route('/ip_worksheet', methods=['GET', 'POST'])
def ip_worksheet():
    if request.method == 'POST':
        session['fqdn'] = request.form.getlist('fqdn[]')
        session['dns'] = request.form.getlist('dns[]')
        session['certificate'] = request.form.getlist('certificate[]')
        session['purpose'] = request.form.getlist('purpose[]')
        session['customer_allocation'] = request.form.getlist('customer_allocation[]')
        return redirect(url_for('firewall_policy_1'))
    return render_template('ip_worksheet.html')

@app.route('/firewall_policy_1', methods=['GET', 'POST'])
def firewall_policy_1():
    if request.method == 'POST':
        session['firewall1_data'] = request.form.to_dict()
        return redirect(url_for('firewall_policy_worksheet_2'))
    return render_template('firewall_policy1.html', rows=[{}])

@app.route('/firewall-policy-worksheet-2', methods=['GET', 'POST'])
def firewall_policy_worksheet_2():
    if request.method == 'POST':
        session['firewall2_data'] = request.form.to_dict()
        return redirect(url_for('network_design'))
    return render_template('firewall_policy2.html')

@app.route('/network-design', methods=['GET', 'POST'])
def network_design():
    if request.method == 'POST':
        if 'networkImage' in request.files:
            file = request.files['networkImage']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                session['uploaded_image'] = filename
        return redirect(url_for('ipsec'))
    
    uploaded_image = session.get('uploaded_image')
    return render_template('network_design.html', uploaded_image=uploaded_image)

@app.route('/ipsec', methods=['GET', 'POST'])
def ipsec():
    if request.method == 'POST':
        session['ipsec_data'] = request.form.to_dict()
    return render_template('ipsec.html')

@app.route('/download_pdf')
def download_pdf():
    # Get all data from session
    customer_name = session.get('customer_name', '')
    short_name = session.get('short_name', '')
    type_value = session.get('type_value', '')
    pcp_type = session.get('pcp_type', '')
    uploaded_image = session.get('uploaded_image', '')

    # Get static files paths
    static_dir = os.path.abspath('static')
    image_map = {
        'PCP-A': 'pcp_a_diagram.png',
        'PCP-B': 'pcp_b_diagram.png',
        'PCP-C': 'pcp_c_diagram.png',
        'PCP-D': 'pcp_d_diagram.png',
    }
    network_diagram_file = image_map.get(pcp_type, 'pcp_a_diagram.png')
    network_diagram_path = f'file://{os.path.join(static_dir, network_diagram_file)}'
    logo_path = f'file://{os.path.join(static_dir, "logo.png")}'
    css_path = f'file://{os.path.join(static_dir, "styles.css")}'

    # Render all templates with hide_buttons=True
    templates = [
        ('introduction.html', {
            'customer_name': customer_name,
            'short_name': short_name,
            'type_value': type_value,
            'pcp_type': pcp_type,
            'hide_buttons': True
        }),
        ('physical_layer_1.html', {
            'pcp_type': pcp_type,
            'customer_name': customer_name,
            'network_diagram_path': network_diagram_path,
            'logo_path': logo_path,
            'css_path': css_path,
            'hide_buttons': True
        }),
        ('ip_worksheet.html', {'hide_buttons': True}),
        ('firewall_policy1.html', {'hide_buttons': True, 'rows': [{}]}),
        ('firewall_policy2.html', {'hide_buttons': True}),
        ('network_design.html', {
            'uploaded_image': uploaded_image,
            'hide_buttons': True
        }),
        ('ipsec.html', {'hide_buttons': True})
    ]

    # Combine all HTML with page breaks
    combined_html = ""
    for template, context in templates:
        html = render_template(template, **context)
        combined_html += html + '<div style="page-break-after: always;"></div>'

    # Generate PDF
    pdf = pdfkit.from_string(combined_html, False, options=PDFKIT_OPTIONS, configuration=PDFKIT_CONFIG)

    # Create response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={customer_name}_network_documentation.pdf'
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5055, debug=True)