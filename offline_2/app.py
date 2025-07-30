from flask import Flask, request, jsonify, send_from_directory
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for PNG output without GUI
import matplotlib.pyplot as plt
import numpy as np
import uuid
import os

app = Flask(__name__)

stored_traces = []
stored_heatmaps = []

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/collect_trace', methods=['POST'])
def collect_trace():
    try:
        req_data = request.get_json()
        trace_data = req_data.get("trace")
        if not trace_data:
            return jsonify({"error": "No trace data provided"}), 400

        # Save trace stats first
        stored_traces.append(trace_data)

        # Reshape and visualize
        arr = np.array(trace_data).reshape(1, -1)
        fig, ax = plt.subplots(figsize=(12, 1.5))
        ax.axis('off')
        ax.imshow(arr, cmap='hot', aspect='auto')

        # Save heatmap image
        img_id = str(uuid.uuid4())
        img_name = f"{img_id}.png"
        img_path = os.path.join("static", "heatmaps", img_name)
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        plt.savefig(img_path, bbox_inches='tight', pad_inches=0)
        plt.close()

        stored_heatmaps.append(img_name)

        return jsonify({
            "image_url": f"/static/heatmaps/{img_name}",
            "min": int(np.min(arr)),
            "max": int(np.max(arr)),
            "samples": len(trace_data)
        })

    except Exception as err:
        return jsonify({"error": str(err)}), 500
    
@app.route('/api/get_traces', methods=['GET'])
def get_traces():
    return jsonify(stored_traces), 200
@app.route('/api/clear_results', methods=['POST'])
def clear_results():
    stored_traces.clear()
    stored_heatmaps.clear()
    return jsonify({"message": "Results cleared."}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
