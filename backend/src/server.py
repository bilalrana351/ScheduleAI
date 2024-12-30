from flask import Flask, request, jsonify
from src.schedulers.ac3 import ac3_schedule
from src.schedulers.forward_checking import forward_checking_schedule
from src.schedulers.backtracking import backtracking_slot_placement
from src.schedulers.greedy_scheduler import fit_tasks_into_schedule
from src.schedulers.interval_scheduler import interval_schedule
from datetime import datetime
from config import DEV
from src.hmms.inference.infer import infer
from flask_cors import CORS

app = Flask(__name__)
# Updated CORS configuration
allowed_origins = ["*"] if DEV else ["http://localhost:3000", "http://127.0.0.1:3000"]

CORS(app, 
     resources={
         r"/*": {
             "origins": allowed_origins,
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }
     })

@app.after_request
def after_request(response):
    # In dev mode, allow any origin, otherwise restrict to localhost:3000
    origin = request.headers.get('Origin')
    if DEV:
        response.headers.add('Access-Control-Allow-Origin', origin or '*')
    else:
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/infer', methods=['POST'])
def process_natural_language():
    try:
        data = request.json
        print(data, "is the data")
        if 'text' not in data:
            return jsonify({'error': 'Missing text field'}), 400

        # Get the natural language text
        text = data['text']
        
        # Process using HMM model
        result = infer(text)
        
        # Extract relevant information
        task_info = {
            'task_name': '',
            'duration': '',
            'time_of_day': '',
            'duration_unit': ''
        }
        
        # Process the state sequence to extract information
        current_activity = []
        for state, word in result['state_sequence_with_words']:
            if state == 'A':  # Activity name
                current_activity.append(word)
            elif state == 'T':  # Time value
                task_info['duration'] = word
            elif state == 'D':  # Duration unit
                task_info['duration_unit'] = word
            elif state == 'P':  # Time period
                task_info['time_of_day'] = word
        
        # Join activity words to form task name
        task_info['task_name'] = ' '.join(current_activity).strip()

        print("DATA")
        
        return jsonify({
            'parsed_info': task_info,
            'raw_inference': result
        })
        
    except Exception as e:
        if DEV:
            raise e
        return jsonify({'error': str(e)}), 500

@app.route('/schedule/<algo>', methods=['POST'])
def schedule(algo):
    try:
        data = request.json

        print(data, "is the data")
        
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
        elif algo == 'backtrack':
            result = backtracking_slot_placement(wake_up, sleep, obligations, tasks)
        elif algo == 'greedy':
            result = fit_tasks_into_schedule(wake_up, sleep, obligations, tasks)
        else:
            if DEV:
                raise ValueError(f"Invalid algorithm: {algo}")
            else:
                return jsonify({'error': f'Invalid algorithm: {algo}'}), 400
            
        preference_respected = result['preference_respected']

        interval_scheduler_used = False
            
        if result['tasks'] is None or len(result['tasks']) != len(tasks):
            # If we couldn't find a schedule, try to use interval scheduler
            result = interval_schedule(wake_up, sleep, obligations, tasks)
            preference_respected = result['preference_respected']
            interval_scheduler_used = True

        result = result['tasks']
            
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
            } for obl in obligations],
            'found_schedule': len(result) > 0,
            'preference_respected': preference_respected,
            'alternative_scheduler_used': interval_scheduler_used
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