from flask import Flask, request, jsonify
from src.schedulers.ac3 import ac3_schedule
from src.schedulers.forward_checking import forward_checking_schedule
from src.schedulers.backtracking import backtracking_slot_placement
from src.schedulers.greedy_scheduler import fit_tasks_into_schedule
from datetime import datetime
from config import DEV
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/schedule/<algo>', methods=['POST'])
def schedule(algo):
    try:
        data = request.json
        
        # Convert string times to datetime.time objects
        wake_up = datetime.strptime(data['wake_up_time'], "%H:%M").time()
        sleep = datetime.strptime(data['sleep_time'], "%H:%M").time()
        
        # Convert obligation times
        obligations = []
        for obligation in data['obligations']:
            obligations.append({
                'task': obligation['task'],
                'start': datetime.strptime(obligation['start'], "%H:%M").time(),
                'end': datetime.strptime(obligation['end'], "%H:%M").time()
            })
        
        # Tasks are already in correct format
        tasks = data['regular_tasks']
        
        # Call appropriate scheduler based on algo parameter
        if algo == 'ac3':
            result = ac3_schedule(wake_up, sleep, obligations, tasks)
        elif algo == 'forward_check':
            result = forward_checking_schedule(wake_up, sleep, obligations, tasks)
        elif algo == 'backward':
            result = backtracking_slot_placement(wake_up, sleep, obligations, tasks)
        elif algo == 'greedy':
            result = fit_tasks_into_schedule(wake_up, sleep, obligations, tasks)
        else:
            if DEV:
                raise ValueError(f"Invalid algorithm: {algo}")
            else:
                return jsonify({'error': f'Invalid algorithm: {algo}'}), 400
            
        if result is None:
            raise ValueError("Could not find a valid schedule")
            
        # Convert datetime.time objects to string format in response
        formatted_result = []
        for task in result:
            formatted_result.append({
                'task': task['task'],
                'start': task['start'].strftime("%H:%M"),
                'end': task['end'].strftime("%H:%M")
            })
            
        return jsonify({
            'schedule': formatted_result,
            'obligations': [{
                'task': obl['task'],
                'start': obl['start'].strftime("%H:%M"),
                'end': obl['end'].strftime("%H:%M")
            } for obl in obligations]
        })
        
    except KeyError as e:
        if DEV:
            raise ValueError(f"Missing required field: {str(e)}")
        else:
            return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except ValueError as e:
        if DEV:
            raise ValueError(f"Invalid data format: {str(e)}")
        else:
            return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        if DEV:
            raise ValueError(f"Server error: {str(e)}")
        else:
            return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=DEV)