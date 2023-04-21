from flask import Flask, jsonify, render_template
import psutil
import nvidia_smi
import wmi
import platform
import pythoncom

app = Flask(__name__)

# Initialize nvidia-smi
nvidia_smi.nvmlInit()

def check_process_running(process_name):
    """
    Check if a process is running by its name.
    :param process_name: The name of the process to check.
    :return: True if the process is running, False otherwise.
    """
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.name() == process_name:
            return True
    return False

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
    if platform.system() == 'Windows':
        # Check if OpenHardwareMonitor process is running
        if not check_process_running('OpenHardwareMonitor.exe'):
            # print("OpenHardwareMonitor is not running. CPU temperature is not monitored.")
            cpu_temperature = -1
        else:
            pythoncom.CoInitialize()
            # Get CPU temperature
            w = wmi.WMI(namespace='root\OpenHardwareMonitor')
            temperatures = w.Sensor()
            cpu_temperature = [sensor.Value for sensor in temperatures if sensor.SensorType=="Temperature" and "cpu" in sensor.Name.lower()]
    else:
        # Get CPU temperature
        temperatures = psutil.sensors_temperatures()
        cpu_temperature = [x.current for x in temperatures['coretemp']]

    # Get RAM usage
    ram_stats = psutil.virtual_memory()
    available_memory = ram_stats.available >> 20
    total_memory = ram_stats.total >> 20
    used_memory = total_memory - available_memory

    # Return the system status as a JSON response
    system_status = {
        'cpu_usage': cpu_usage,
        'cpu_temperature': cpu_temperature,
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