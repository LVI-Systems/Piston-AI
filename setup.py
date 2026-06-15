#!/bin/python3
import subprocess
import socket

def installPackages() -> bool:
    try:
        subprocess.run("pip3 install -r requirements.txt --break-system-packages".split(), check=True)
        print("Successfully installed depencies.")
        return True
    except Exception as e:
        print(f"Error installing depencies: {e}")
        return False
    
def OTIDB():
    print("""
""")
    choice = input("Would you like to enable local database? [y/n, default=n]")
    if not choice.strip() or choice.lower() == "y":
        ipAddress = input("IP address to database (Leave blank to cancel): ")
        if ipAddress:
            port = input("SSH port [default=22]: ")
            if not port:
                port = "22"
            result = checkSSH(ipAddress, port, 3)
            if result:
                print(f"SSH port of {ipAddress} is reachable.")
                return True
            else:
                print(f"SSH port of {ipAddress} is unreachable. Local database will not be set up.")
                return False
        elif not ipAddress.strip():
            print(f"Local database will not be set up.")
            return False

    else:
        print("Local database will not be set up.")
    
def checkSSH(host="0.0.0.0", port="22", timeout=3):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            result = s.connect_ex((host, port))
            return result == 0
        except:
            return False
        
def OTIDBInternalSetup():
    # Don't peek in here bro I'm not done yet
    pass

def main():
    installPackagesResult = installPackages()
    if not installPackagesResult:
        return
    #OTIDBResult = OTIDB()
    #if OTIDBResult:
    #    OTIDBInternalSetup()



if __name__ == "__main__":
    main()