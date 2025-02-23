import os
import platform
import subprocess
import webbrowser

def main():
    """ Sphinx 문서를 빌드하고 성공하면 HTML 파일을 자동으로 엽니다. """
    if platform.system() == "Windows":
        command = ["cmd", "/c", "make.bat", "html"]
        index_path = "docs\\sphinx\\build\\html\\index.html"
    else:
        command = ["make", "html"]
        index_path = "docs/sphinx/build/html/index.html"
    
    try:
        subprocess.run(command, check=True, cwd="docs/sphinx")
        print("✅ Sphinx 문서 빌드 완료!")
        
        # 빌드 성공 시 자동으로 문서 열기
        if os.path.exists(index_path):
            webbrowser.open(index_path)
        else:
            print("⚠️ 빌드된 index.html을 찾을 수 없습니다.")
    except subprocess.CalledProcessError:
        print("❌ Sphinx 문서 빌드 실패!")
        exit(1)

if __name__ == "__main__":
    main()

