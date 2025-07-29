# Updated app1.py with UI and file upload
from flask import Flask, render_template, request
import subprocess
import shutil
import os
from pathlib import Path

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to read the first line from procname.txt
def get_first_procname(proc_file: Path) -> str:
    with proc_file.open('r') as file:
        return file.readline().strip()

def run_rrrMMU_and_save_output(procname: str, try_dir: Path, output_dir: Path):
    rrrMMU_exec = try_dir / 'rrrMMU'
    input_file = try_dir / f'{procname}.1'
    map_file = try_dir / '31750fuse.map'
    output_file = try_dir / f'{procname}.2'

    command = f"./rrrMMU {input_file} {map_file} > {output_file}"
    print(f"Running command: {command} in {try_dir}")
    subprocess.run(command, shell=True, check=True, cwd=try_dir)

    target_file = output_dir / f"{procname}.2"
    shutil.copy(output_file, target_file)
    print(f"Output saved to: {target_file}")

def run_exe_using_bash(procname: str, base_dir: str, output_dir: str):
    output_file = os.path.join(output_dir, f"{procname}.1")
    bash_script_content = f"""#!/bin/bash
cd \"{base_dir}\"
./exe \"{procname}\" \"try/rmtpgmpaa.lst\" > \"{output_file}\"
echo \"Output saved to backend_two/{procname}.1\"
"""
    script_path = os.path.join(output_dir, 'run_exe.sh')
    with open(script_path, 'w') as bash_file:
        bash_file.write(bash_script_content)
    os.chmod(script_path, 0o755)
    try:
        subprocess.run([script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run bash script: {e}")

def main():
    current_file = Path(__file__).resolve()
    backend_two_dir = current_file.parent
    soumya_dir = backend_two_dir.parent
    try_dir = soumya_dir / 'try'
    proc_file = try_dir / 'procname.txt'
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_dir = os.path.join(base_dir, 'backend_two')

    procname = get_first_procname(proc_file)
    print(f"Running rrrMMU for: {procname}")
    run_rrrMMU_and_save_output(procname, try_dir, backend_two_dir)
    print(f"Running exe for: {procname}")
    run_exe_using_bash(procname, base_dir, output_dir)

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        for i in range(1, 4):
            file = request.files.get(f'file{i}')
            if file:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        main()  # Call main after files are uploaded
        return "Files uploaded and processing complete."
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
