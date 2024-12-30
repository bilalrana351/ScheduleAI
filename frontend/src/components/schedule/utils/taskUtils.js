import { calculateRemainingTime } from './timeUtils';

export const validateTaskDuration = (duration, unit, scheduleData) => {
  if (!duration) return "";
  
  // Convert duration to minutes for comparison
  const durationInMinutes = unit === 'hours' ? parseInt(duration) * 60 : parseInt(duration);
  const remainingTime = calculateRemainingTime(
    scheduleData.wakeTime,
    scheduleData.sleepTime,
    scheduleData.obligations,
    scheduleData.tasks
  );

  if (durationInMinutes > remainingTime) {
    return `Task duration exceeds available time (${Math.floor(remainingTime / 60)}h ${remainingTime % 60}m remaining)`;
  }
  return "";
};

export const parseNaturalLanguageInput = (text) => {
  // Parse duration from text (e.g., "2 hours", "30 minutes", "2.5 hours")
  const hourPattern = /(\d+\.?\d*)\s*(?:hours?|hrs?|h)/i;
  const minutePattern = /(\d+)\s*(?:minutes?|mins?|m)/i;
  
  let durationInMinutes = 0;
  const hoursMatch = text.match(hourPattern);
  const minutesMatch = text.match(minutePattern);

  if (hoursMatch) {
    durationInMinutes += parseFloat(hoursMatch[1]) * 60;
  }
  if (minutesMatch) {
    durationInMinutes += parseInt(minutesMatch[1]);
  }

  // Extract task name (everything before the duration)
  let taskName = text;
  if (hoursMatch || minutesMatch) {
    taskName = text.split(/\s+(?:\d+\.?\d*\s*(?:hours?|hrs?|h|minutes?|mins?|m))/i)[0].trim();
  }

  return {
    taskName,
    durationInMinutes: durationInMinutes > 0 ? durationInMinutes.toString() : ''
  };
}; 