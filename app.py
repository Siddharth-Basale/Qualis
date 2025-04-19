from flask import Flask, render_template, request, redirect, url_for, make_response, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16 MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['SECRET_KEY'] = 'your_secret_key'

# Configure path to wkhtmltopdf binary


# PDFKit options
PDFKIT_OPTIONS = {
    'enable-local-file-access': '',
    'quiet': ''
}

@app.route('/', methods=['GET', 'POST'])
def pcp_type_selection():
    if request.method == 'POST':
        pcp_type = request.form['pcp_type']
        return redirect(url_for('customer_details', pcp_type=pcp_type))
    return render_template('pcp_type_selection.html')

@app.route('/customer_details', methods=['GET', 'POST'])
def customer_details():
    pcp_type = request.args.get('pcp_type')
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        short_name = request.form['short_name']
        type_value = request.form['type']
        return redirect(url_for('introduction', customer_name=customer_name, short_name=short_name, type_value=type_value, pcp_type=pcp_type))
    return render_template('customer_details.html', pcp_type=pcp_type)


@app.route('/introduction')
def introduction():
    customer_name = request.args.get('customer_name')
    short_name = request.args.get('short_name')
    type_value = request.args.get('type_value')
    pcp_type = request.args.get('pcp_type')
    return render_template('introduction.html', customer_name=customer_name, short_name=short_name, type_value=type_value, pcp_type=pcp_type)

@app.route('/physical_layer_1', methods=['POST'])
def physical_layer_1():
    pcp_type = request.args.get('pcp_type', 'PCP-A')
    customer_name = request.args.get('customer_name', '')

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

# 🛠 This should now be correctly placed outside
#@app.route('/ip-worksheet')
#def ip_worksheet():
#    return render_template('ip_worksheet.html')

@app.route('/ip_worksheet', methods=['GET', 'POST'])
def ip_worksheet():
    if request.method == 'POST':
        fqdn = request.form.getlist('fqdn[]')
        dns = request.form.getlist('dns[]')
        certificate = request.form.getlist('certificate[]')
        purpose = request.form.getlist('purpose[]')
        customer_allocation = request.form.getlist('customer_allocation[]')

        # Process/save this data as needed
        print(fqdn, dns, certificate, purpose, customer_allocation)

        return redirect(url_for('firewall_policy_1'))

    return render_template('ip_worksheet.html')


@app.route('/firewall_policy_1', methods=['GET', 'POST'])
def firewall_policy_1():
#    return "<h2>Firewall Policy Worksheet 1 - Coming Soon</h2>"
    if request.method == 'POST':
        return redirect(url_for('firewall_policy_1'))

    rows = [{
        'protocol': '', 'source_ip': '', 'source_port': '', 'direction': '',
        'fqdn_service': '', 'dest_ip': '', 'dest_port': '', 'purpose': ''
    }]
    return render_template('firewall_policy1.html', rows=rows)


@app.route('/firewall-policy-worksheet-2', methods=['POST'])
def firewall_policy_worksheet_2():
    # Process the form data from Firewall Policy Worksheet 1
    fqdn_input = request.form.get('fqdnInput')
    ip_base_input = request.form.get('ipBaseInput')
    # Handle other inputs as needed
    print(f"FQDN Input: {fqdn_input}, IP Base Input: {ip_base_input}")

    # Now render Firewall Policy Worksheet 2
    return render_template('firewall_policy2.html')  # Replace with your second worksheet template

@app.route('/network-design', methods=['GET', 'POST'])
def network_design():
    uploaded_image = None

    if request.method == 'POST':
        if 'networkImage' in request.files:
            file = request.files['networkImage']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_image = filename
                session['uploaded_image'] = uploaded_image  # Store in session

    # On GET or after POST
    uploaded_image = session.get('uploaded_image')
    return render_template('network_design.html', uploaded_image=uploaded_image)

@app.route('/ipsec', methods=['GET', 'POST'])
def ipsec():
    return render_template('ipsec.html')


@app.route('/download_pdf')
def download_pdf():
    customer_name = request.args.get('customer_name')
    pcp_type = request.args.get('pcp_type')

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

    # Render both HTML pages
    introduction_html = render_template('introduction.html', customer_name=customer_name, pcp_type=pcp_type)
    physical_layer_html = render_template(
        'physical_layer_1.html',
        pcp_type=pcp_type,
        customer_name=customer_name,
        network_diagram_path=network_diagram_path,
        logo_path=logo_path,
        css_path=css_path
    )

    # Add page break between sections
    combined_html = introduction_html + '<div style="page-break-after: always;"></div>' + physical_layer_html

    # Generate PDF
    pdf = pdfkit.from_string(combined_html, False, options=PDFKIT_OPTIONS, configuration=PDFKIT_CONFIG)

    # Return response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=network_diagram.pdf'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5055, debug=True)

