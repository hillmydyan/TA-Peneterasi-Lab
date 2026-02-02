import subprocess
from config import Config

def reset_vm_to_snapshot(vm_name: str, snapshot_name: str) -> dict:
    """Reset VM ke snapshot tertentu menggunakan VBoxManage."""
    vbox_cmd = Config.VBOX_PATH
    
    try:
        # Power off VM terlebih dahulu (force poweroff)
        subprocess.run([vbox_cmd, 'controlvm', vm_name, 'poweroff'], 
                      capture_output=True, timeout=30)
        
        # Restore snapshot
        result = subprocess.run(
            [vbox_cmd, 'snapshot', vm_name, 'restore', snapshot_name],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0:
            # Start VM kembali (headless mode)
            subprocess.run([vbox_cmd, 'startvm', vm_name, '--type', 'headless'],
                          capture_output=True, timeout=30)
            return {'success': True, 'message': 'VM berhasil di-reset ke snapshot'}
        else:
            # Jika error, kirim pesan error dari stderr
            error_msg = result.stderr.strip() if result.stderr else "Unknown error occurred"
            return {'success': False, 'message': f"Gagal restore snapshot: {error_msg}"}
            
    except subprocess.TimeoutExpired:
        return {'success': False, 'message': "Proses timeout saat mencoba reset VM"}
    except Exception as e:
        return {'success': False, 'message': f"System Error: {str(e)}"}

def start_vm_headless(vm_name: str) -> dict:
    """Menyalakan VM dalam mode headless jika belum menyala."""
    vbox_cmd = Config.VBOX_PATH
    try:
        # Cek status VM
        status = subprocess.run([vbox_cmd, 'showvminfo', vm_name, '--machinereadable'],
                              capture_output=True, text=True)
        if 'VMState="running"' in status.stdout:
             return {'success': True, 'message': 'VM sudah berjalan'}

        # Start VM
        subprocess.run([vbox_cmd, 'startvm', vm_name, '--type', 'headless'],
                      capture_output=True, timeout=30)
        return {'success': True, 'message': 'VM berhasil dinyalakan'}
    except Exception as e:
        return {'success': False, 'message': str(e)}