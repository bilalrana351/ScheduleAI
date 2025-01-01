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

  return "";
};

export const validateTimeSelection = (startTime, endTime, wakeTime, sleepTime, obligations) => {
  const start = convertToMinutes(startTime);
  let end = convertToMinutes(endTime);
  const wake = convertToMinutes(wakeTime);
  let sleep = convertToMinutes(sleepTime);

  // Add the case where the sleep time is less than the wake time
  if (sleep < wake) {
    sleep += 24 * 60;
  }

  // If end time is before start time, add 24 hours to end time
  if (end < start) {
    end += 24 * 60; // Add 24 hours worth of minutes
  }

  console.log("start", start);
  console.log("end", end);
  console.log("wake", wake);
  console.log("sleep", sleep);

  // Check if time is outside wake/sleep time
  if (start < wake || end > sleep) {
    return { error: "Selected time is outside your wake/sleep schedule", warning: "" };
  }

  // Calculate duration of new obligation
  const newObligationDuration = end - start;

  // Calculate remaining time including existing obligations
  const remainingTime = calculateRemainingTime(wakeTime, sleepTime, obligations, []);

  // Check if new obligation exceeds remaining time
  if (newObligationDuration > remainingTime) {
    return { 
      error: `This obligation exceeds available time (${Math.floor(remainingTime / 60)}h ${remainingTime % 60}m remaining)`, 
      warning: "" 
    };
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
  const totalDayMinutes = 24 * 60;

  // Sort obligations by start time
  const sortedObligations = [...obligations].sort((a, b) => 
    convertToMinutes(a.startTime) - convertToMinutes(b.startTime)
  );

  // Calculate available time slots
  let availableMinutes = 0;
  let lastEndTime = wakeMinutes;

  // Handle case where sleep time is less than wake time (crosses midnight)
  const isCrossingMidnight = sleepMinutes < wakeMinutes;
  const adjustedSleepMinutes = isCrossingMidnight ? sleepMinutes + totalDayMinutes : sleepMinutes;

  // Add time slots between obligations
  for (const obligation of sortedObligations) {
    let oblStart = convertToMinutes(obligation.startTime);
    let oblEnd = convertToMinutes(obligation.endTime);

    // Adjust obligation times if they cross midnight
    if (isCrossingMidnight && oblStart < wakeMinutes) {
      oblStart += totalDayMinutes;
      oblEnd += totalDayMinutes;
    }
    
    // Add the gap before this obligation
    if (oblStart > lastEndTime) {
      availableMinutes += oblStart - lastEndTime;
    }
    
    lastEndTime = Math.max(lastEndTime, oblEnd);
  }

  // Add remaining time after last obligation until sleep
  if (lastEndTime < adjustedSleepMinutes) {
    availableMinutes += adjustedSleepMinutes - lastEndTime;
  }

  console.log("availableMinutes", availableMinutes);

  // Subtract time taken by existing tasks
  for (const task of tasks) {
    availableMinutes -= parseInt(task.duration);
  }

  console.log("availableMinutes", availableMinutes);

  return availableMinutes;
}; 