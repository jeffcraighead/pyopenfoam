import os
import subprocess
import zipfile
import tempfile
import shutil
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

def run_openfoam_simulation(case_zip_path):
    # Create a temporary directory for the simulation
    with tempfile.TemporaryDirectory() as temp_dir:
        # Unzip the case file into the temporary directory
        with zipfile.ZipFile(case_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Find the extracted case directory (assuming there's only one)
        extracted_dirs = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
        if not extracted_dirs:
            return {"error": "No valid OpenFOAM case found in the zip file."}, 400
        case_dir = temp_dir

        # Ensure necessary OpenFOAM commands are available
        try:
            # Run blockMesh if blockMeshDict exists
            block_mesh_dict_path = os.path.join(case_dir, 'system', 'blockMeshDict')
            if os.path.exists(block_mesh_dict_path):
                subprocess.run(['blockMesh', '-case', case_dir], check=True)

            # Run snappyHexMesh if snappyHexMeshDict exists
            snappy_hex_mesh_dict_path = os.path.join(case_dir, 'system', 'snappyHexMeshDict')
            if os.path.exists(snappy_hex_mesh_dict_path):
                subprocess.run(['snappyHexMesh', '-case', case_dir, '-overwrite'], check=True)

            # Optionally run potentialFoam for better initial conditions
            subprocess.run(['potentialFoam', '-case', case_dir], check=True)

            # Run the main simulation (simpleFoam, pisoFoam, etc.)
            # Choose the solver based on controlDict's application field
            control_dict_path = os.path.join(case_dir, 'system', 'controlDict')
            with open(control_dict_path, 'r') as f:
                for line in f:
                    if 'application' in line:
                        solver = line.split()[-1].strip(';')
                        break
            subprocess.run([solver, '-case', case_dir], check=True)

        except subprocess.CalledProcessError as e:
            return {"error": f"Error running OpenFOAM command: {str(e)}"}, 500
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}, 500

        # Compress the results to send back
        results_zip_path = os.path.join(temp_dir, 'results.zip')
        with zipfile.ZipFile(results_zip_path, 'w') as zipf:
            for root, _, files in os.walk(case_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, case_dir))

    # Return the path to the compressed results
    return results_zip_path

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.zip'):
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            file.save(temp_zip.name)
            try:
                # Run the simulation
                results_path = run_openfoam_simulation(temp_zip.name)
                if isinstance(results_path, tuple):
                    return jsonify(results_path[0]), results_path[1]  # Handle error response

                # Send the compressed results back to the client
                return send_file(results_path, as_attachment=True, download_name='results.zip')

            finally:
                # Cleanup: Remove the temporary zip file
                os.remove(temp_zip.name)

    return jsonify({"error": "Invalid file format, only .zip files are allowed."}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
