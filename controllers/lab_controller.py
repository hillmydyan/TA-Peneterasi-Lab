from flask import Blueprint, render_template, jsonify, request
from datetime import datetime
import os
from flask_login import login_required, current_user
from config import Config
from services.vm_reset_service import reset_vm_to_snapshot, start_vm_headless

lab = Blueprint("lab", __name__)

if not os.path.exists("logs"):
    os.makedirs("logs")

def simpan_log(aksi):
    with open("logs/aktivitas.log", "a") as f:
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{waktu} - {aksi}\n")

# =========================
# LAB DDOS
# =========================
@lab.route("/lab/ddos")
@login_required
def ddos_design():
    simpan_log("Akses LAB DDOS")
    
    # Ambil Config
    guac_url = Config.GUACAMOLE_URL
    ids = Config.GUAC_CONNECTIONS.get('ddos', {})
    
    attacker_url = f"{guac_url}/#/client/{ids.get('attacker', '')}"
    target_url = f"{guac_url}/#/client/{ids.get('target', '')}"

    return render_template("lab/ddos.html", attacker_url=attacker_url, target_url=target_url)

# =========================
# LAB SNIFFING
# =========================
@lab.route("/lab/sniffing")
@login_required
def sniffing_design():
    simpan_log("Akses LAB Sniffing")
    
    guac_url = Config.GUACAMOLE_URL
    ids = Config.GUAC_CONNECTIONS.get('sniffing', {})
    
    attacker_url = f"{guac_url}/#/client/{ids.get('attacker', '')}"
    target_url = f"{guac_url}/#/client/{ids.get('target', '')}"
    
    return render_template("lab/sniffing.html", attacker_url=attacker_url, target_url=target_url)

# =========================
# LAB DNS SPOOFING
# =========================
@lab.route("/lab/dns-spoofing")
@login_required
def dns_spoofing_design():
    simpan_log("Akses LAB DNS Spoofing")
    
    guac_url = Config.GUACAMOLE_URL
    ids = Config.GUAC_CONNECTIONS.get('dns_spoofing', {})
    
    attacker_url = f"{guac_url}/#/client/{ids.get('attacker', '')}"
    target_url = f"{guac_url}/#/client/{ids.get('target', '')}"
    
    return render_template("lab/dns-spoofing.html", attacker_url=attacker_url, target_url=target_url)

# =========================
# VM RESET ENDPOINT
# =========================
@lab.route("/lab/<lab_name>/reset", methods=["POST"])
@login_required
def reset_vm(lab_name):
    simpan_log(f"Request Reset VM untuk Lab: {lab_name}")
    
    # Validasi Lab Name
    if lab_name not in Config.VM_SNAPSHOTS:
        return jsonify({'success': False, 'message': 'Lab tidak ditemukan'}), 404
        
    vm_config = Config.VM_SNAPSHOTS[lab_name].get('target')
    if not vm_config:
         return jsonify({'success': False, 'message': 'Konfigurasi VM tidak ditemukan'}), 404
         
    vm_name = vm_config.get('vm_name')
    snapshot = vm_config.get('snapshot')
    
    if not vm_name or not snapshot:
        return jsonify({'success': False, 'message': 'Konfigurasi VM belum lengkap'}), 500
        
    # Lakukan Reset
    result = reset_vm_to_snapshot(vm_name, snapshot)
    
    if result['success']:
        simpan_log(f"Berhasil Reset VM {vm_name} ke Snapshot {snapshot}")
    else:
        simpan_log(f"Gagal Reset VM {vm_name}: {result['message']}")
        
    return jsonify(result)

# =========================
# VM START ENDPOINT
# =========================
@lab.route("/lab/<lab_name>/start", methods=["POST"])
@login_required
def start_vm_route(lab_name):
    # Ambil JSON
    data = request.get_json(silent=True) or {}
    vm_type = data.get('vm_type', 'target')  # Default ke 'target' untuk backward compatibility
    
    simpan_log(f"Request Start VM ({vm_type}) untuk Lab: {lab_name}")
    
    # Validasi Lab Name
    if lab_name not in Config.VM_SNAPSHOTS:
        return jsonify({'success': False, 'message': 'Lab tidak ditemukan'}), 404
        
    vm_config = Config.VM_SNAPSHOTS[lab_name].get(vm_type)
    if not vm_config:
         return jsonify({'success': False, 'message': f'Konfigurasi VM {vm_type} tidak ditemukan'}), 404
         
    vm_name = vm_config.get('vm_name')
    
    if not vm_name:
        return jsonify({'success': False, 'message': 'Nama VM belum dikonfigurasi'}), 500
        
    # Lakukan Start VM
    result = start_vm_headless(vm_name)
    
    if result['success']:
        simpan_log(f"Berhasil Start VM {vm_name}")
    else:
        simpan_log(f"Gagal Start VM {vm_name}: {result['message']}")
        
    return jsonify(result)