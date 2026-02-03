from flask import Blueprint, render_template

forensic_bp = Blueprint('forensic', __name__)

@forensic_bp.route('/lab/forensic')
def index():
    return render_template('lab/digital_forensic/main.html')

@forensic_bp.route('/lab/forensic/module/digital-forensic')
def digital_forensic_intro():
    return render_template('lab/digital_forensic/module/digital-forensic.html')

@forensic_bp.route('/lab/forensic/module/network-forensic')
def network_forensic():
    return render_template('lab/digital_forensic/module/network-forensic.html')

@forensic_bp.route('/lab/forensic/module/file-analysis')
def file_analysis():
    return render_template('lab/digital_forensic/module/file-analysis.html')

@forensic_bp.route('/lab/forensic/module/digital-footprint')
def digital_footprint():
    return render_template('lab/digital_forensic/module/digital-footprint.html')

@forensic_bp.route('/lab/forensic/practice')
def practice():
    # Placeholder
    return render_template('lab/digital_forensic/practice.html')

