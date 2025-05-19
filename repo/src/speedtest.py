import subprocess

def run_speedtest():
    # Test básico
    print("\n[+] Test Completo:")
    subprocess.run(["speedtest-cli"], check=True)
    
    # Test simplificado
    print("\n[+] Test Resumido:")
    subprocess.run(["speedtest-cli", "--simple"], check=True)

if __name__ == "__main__":
    run_speedtest()