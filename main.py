from flask import Flask, jsonify, render_template
import psutil
import nvidia_smi

app = Flask(__name__)

# Initialize nvidia-smi
nvidia_smi.nvmlInit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    # Get GPU temperature and usage
    handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
    gpu_temperature = nvidia_smi.nvmlDeviceGetTemperature(handle, 0)
    memory_info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
    gpu_usage = nvidia_smi.nvmlDeviceGetUtilizationRates(handle).gpu
    gpu_power = nvidia_smi.nvmlDeviceGetPowerUsage(handle)

    # Get CPU usage
    cpu_usage = psutil.cpu_percent()

    # Get RAM usage
    ram_stats = psutil.virtual_memory()
    available_memory = ram_stats.available >> 20
    total_memory = ram_stats.total >> 20
    used_memory = total_memory - available_memory

    # Return the system status as a JSON response
    system_status = {
        'cpu_usage': cpu_usage,
        'gpu_usage': gpu_usage,
        'gpu_power': gpu_power,
        'gpu_temperature': gpu_temperature,
        'gpu_memory_usage': memory_info.used,
        'gpu_memory_total': memory_info.total,
        'ram_usage': used_memory,
        'ram_total': total_memory
    }
    return jsonify(system_status)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)