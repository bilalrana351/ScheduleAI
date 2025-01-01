'use client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';

// Simplified headers
const defaultHeaders = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};

const fetchWithCORS = async (url, options) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const inferNaturalLanguage = async (text) => {
  return fetchWithCORS(`${API_URL}/infer`, {
    method: 'POST',
    body: JSON.stringify({ text })
  });
};

export const generateSchedule = async (scheduleData, algorithm = 'ac3') => {
  // Ensure all durations are numbers
  const formattedTasks = scheduleData.tasks.map(task => ({
    task: task.name,
    duration: parseInt(task.duration, 10),
    preference: task.timeOfDay || ''  // Include preference, default to empty string
  }));

  return fetchWithCORS(`${API_URL}/schedule/${algorithm}`, {
    method: 'POST',
    body: JSON.stringify({
      wake_up_time: scheduleData.wakeTime,
      sleep_time: scheduleData.sleepTime,
      obligations: scheduleData.obligations.map(obl => ({
        task: obl.name,
        start: obl.startTime,
        end: obl.endTime
      })),
      regular_tasks: formattedTasks
    })
  });
};