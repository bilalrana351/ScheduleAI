from flask import Flask, request, jsonify
from src.schedulers.ac3 import ac3_schedule
from src.schedulers.forward_checking import forward_checking_schedule
from src.schedulers.backtracking import backtracking_slot_placement
from src.schedulers.greedy_scheduler import fit_tasks_into_schedule
from src.schedulers.interval_scheduler import interval_schedule
from datetime import datetime, timedelta
from config import DEV
from src.hmms.inference.infer import infer
from flask_cors import CORS
from src.core.helpers import split_cross_midnight_obligations, combine_split_obligations
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Updated CORS configuration
# allowed_origins = ["*"] if DEV else ["http://localhost:3000", "http://127.0.0.1:3000"]

# Simpler CORS setup that allows all origins in dev mode
CORS(app)

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

        print(data['obligations'], "is the obligations")
        
        # Convert obligation times
        obligations = []
        for obligation in data['obligations']:
            obligations.append({
                'task': obligation['task'],
                'start': datetime.strptime(obligation['start'], "%H:%M").time(),
                'end': datetime.strptime(obligation['end'], "%H:%M").time()
            })
        

        # Split obligations that cross midnight
        split_obligations = split_cross_midnight_obligations(obligations)
        
        # Tasks are already in correct format
        tasks = data['regular_tasks']
        
        # Call appropriate scheduler based on algo parameter
        if algo == 'ac3':
            result = ac3_schedule(wake_up, sleep, split_obligations, tasks)
        elif algo == 'forward_check':
            result = forward_checking_schedule(wake_up, sleep, split_obligations, tasks)
        elif algo == 'backtrack':
            result = backtracking_slot_placement(wake_up, sleep, split_obligations, tasks)
        elif algo == 'greedy':
            result = fit_tasks_into_schedule(wake_up, sleep, split_obligations, tasks)
        else:
            if DEV:
                raise ValueError(f"Invalid algorithm: {algo}")
            else:
                return jsonify({'error': f'Invalid algorithm: {algo}'}), 400


        interval_scheduler_used = False
            
        if result['found_schedule'] is False:
            # If we couldn't find a schedule, try to use interval scheduler
            result = interval_schedule(wake_up, sleep, split_obligations, tasks)
            interval_scheduler_used = True
        
        if result['found_schedule'] is False:
            if len(result['tasks']) != len(tasks):
                result = interval_schedule(wake_up, sleep, split_obligations, tasks)
                interval_scheduler_used = True

        print(result, "is the result")

        print(result['tasks'], "is the tasks")
                    
        # Combine split obligations back together
        combined_result = combine_split_obligations(result['tasks'])

        print(combined_result, "is the combined result")
            
        # Convert datetime.time objects to string format in response
        formatted_result = []

        for task in combined_result:
            formatted_result.append({
                'task': task['task'],
                'start': task['start'].strftime("%H:%M"),
                'end': task['end'].strftime("%H:%M")
            })

        print(formatted_result, "is the formatted result")

            
        return jsonify({
            'schedule': formatted_result,
            'obligations': [{
                'task': obl['task'],
                'start': obl['start'].strftime("%H:%M"),
                'end': obl['end'].strftime("%H:%M")
            } for obl in obligations],  # Use original obligations here, not split ones
            'found_schedule': result['found_schedule'],
            'preference_respected': result['preference_respected'],
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