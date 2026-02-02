class Config:
    SECRET_KEY = "labvirtual-secret"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Konfigurasi Guacamole
    # Ganti URL sesuai dengan alamat server Guacamole Anda (misal: http://localhost:8080/guacamole)
    GUACAMOLE_URL = "http://localhost:8080"
    
    # Mapping ID Koneksi Guacamole untuk setiap Lab
    # Format: 'lab_name': {'attacker': 'ID_KONEKSI_ATTACKER', 'target': 'ID_KONEKSI_TARGET'}
    # ID Koneksi bisa dilihat di URL Guacamole saat membuka koneksi, misal: client/c/1
    GUAC_CONNECTIONS = {
        'ddos': {
            'attacker': 'MgBjAHBvc3RncmVzcWw=', 
            'target': 'NQBjAHBvc3RncmVzcWw='
        },
    }

    # Konfigurasi Path VBoxManage
    # Jika VBoxManage tidak ada di PATH environment variable, isi full path di sini
    # Contoh Windows: r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
    # Contoh Linux/Mac: "/usr/bin/VBoxManage" (atau biarkan "VBoxManage" jika sudah di PATH)
    VBOX_PATH = r"E:\virtualbox\VBoxManage.exe" 

    # Konfigurasi VM dan Snapshot untuk Reset
    # Ganti 'vm_name' dan 'snapshot' sesuai dengan setup VirtualBox Anda
    VM_SNAPSHOTS = {
        'ddos': {
            'target': {'vm_name': 'target2', 'snapshot': 'clean-target2'},
            'attacker': {'vm_name': 'vm-attaker', 'snapshot': 'clean-attacker'}
        },
        'sniffing': {
            'target': {'vm_name': 'target1', 'snapshot': 'Clean-State'},
            'attacker': {'vm_name': 'vm-attaker', 'snapshot': 'clean-attacker'}
        },
        'dns-spoofing': {  # Perhatikan: key harus match dengan lab_name di controller
            'target': {'vm_name': 'target3', 'snapshot': 'Clean-State'},
            'attacker': {'vm_name': 'vm-attaker', 'snapshot': 'clean-attacker'}
        }
    }
