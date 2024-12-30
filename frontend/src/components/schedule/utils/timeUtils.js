export const convertToMinutes = (time) => {
  const [hours, minutes] = time.split(':').map(Number);
  return hours * 60 + minutes;
};

export const validateTimeFormat = (time) => {
  const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
  return timeRegex.test(time);
};

export const validateSleepTime = (wakeTime, sleepTime) => {
  const wakeMinutes = convertToMinutes(wakeTime);
  const sleepMinutes = convertToMinutes(sleepTime);

  if (sleepMinutes <= wakeMinutes) {
    return "Sleep time must be after wake-up time";
  }
  return "";
};

export const validateTimeSelection = (startTime, endTime, wakeTime, sleepTime, obligations) => {
  const start = convertToMinutes(startTime);
  const end = convertToMinutes(endTime);
  const wake = convertToMinutes(wakeTime);
  const sleep = convertToMinutes(sleepTime);

  // Check if time is outside wake/sleep time
  if (start < wake || end > sleep) {
    return { error: "Selected time is outside your wake/sleep schedule", warning: "" };
  }

  // Check for overlaps with existing obligations
  for (const obligation of obligations) {
    const oblStart = convertToMinutes(obligation.startTime);
    const oblEnd = convertToMinutes(obligation.endTime);

    if (
      (start >= oblStart && start < oblEnd) || // Start time overlaps
      (end > oblStart && end <= oblEnd) || // End time overlaps
      (start <= oblStart && end >= oblEnd) // Completely encompasses an obligation
    ) {
      return { error: "", warning: `This time overlaps with obligation: ${obligation.name}` };
    }
  }

  return { error: "", warning: "" };
};

export const calculateRemainingTime = (wakeTime, sleepTime, obligations, tasks) => {
  const wakeMinutes = convertToMinutes(wakeTime);
  const sleepMinutes = convertToMinutes(sleepTime);

  // Sort obligations by start time
  const sortedObligations = [...obligations].sort((a, b) => 
    convertToMinutes(a.startTime) - convertToMinutes(b.startTime)
  );

  // Calculate available time slots
  let availableMinutes = 0;
  let lastEndTime = wakeMinutes;

  // Add time slots between obligations
  for (const obligation of sortedObligations) {
    const oblStart = convertToMinutes(obligation.startTime);
    const oblEnd = convertToMinutes(obligation.endTime);
    
    // Add the gap before this obligation
    if (oblStart > lastEndTime) {
      availableMinutes += oblStart - lastEndTime;
    }
    
    lastEndTime = Math.max(lastEndTime, oblEnd);
  }

  // Add remaining time after last obligation until sleep
  if (lastEndTime < sleepMinutes) {
    availableMinutes += sleepMinutes - lastEndTime;
  }

  // Subtract time taken by existing tasks
  for (const task of tasks) {
    availableMinutes -= parseInt(task.duration);
  }

  return availableMinutes;
}; 