const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

const defaultHeaders = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

export const inferNaturalLanguage = async (text) => {
  try {
    const response = await fetch(`${API_URL}/infer`, {
      method: 'POST',
      headers: defaultHeaders,
      credentials: 'include',
      mode: 'cors',
      body: JSON.stringify({ text })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Failed to process natural language input');
    }

    const data = await response.json();

    console.log(data);
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const generateSchedule = async (scheduleData, algorithm = 'ac3') => {
  try {
    const response = await fetch(`${API_URL}/schedule/${algorithm}`, {
      method: 'POST',
      headers: defaultHeaders,
      credentials: 'include',
      mode: 'cors',
      body: JSON.stringify({
        wake_up_time: scheduleData.wakeTime,
        sleep_time: scheduleData.sleepTime,
        obligations: scheduleData.obligations.map(obl => ({
          task: obl.name,
          start: obl.startTime,
          end: obl.endTime
        })),
        regular_tasks: scheduleData.tasks.map(task => ({
          task: task.name,
          duration: task.duration
        }))
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Failed to generate schedule');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}; 