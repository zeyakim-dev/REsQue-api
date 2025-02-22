import platform
import subprocess

def main():
    if platform.system() == "Windows":
        command = ["cmd", "/c", "make.bat", "html"]
    else:
        command = ["make", "html"]
    
    try:
        subprocess.run(command, check=True, cwd="docs/sphinx")
        print("✅ Sphinx 문서 빌드 완료!")
    except subprocess.CalledProcessError:
        print("❌ Sphinx 문서 빌드 실패!")
        exit(1)

if __name__ == "__main__":
    main()
