export const convertToMinutes = (time) => {
  console.log("Tiadsfadsme", time, typeof time);
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

export const createSleepSlots = (wakeTime, sleepTime) => {
  const wake = convertToMinutes(wakeTime);
  let sleep = convertToMinutes(sleepTime);
  const MIDNIGHT_END = 24 * 60 - 1;    // 23:59
  const MIDNIGHT_START = 0;            // 00:00
  
  // Handle edge case where wake and sleep are the same time
  if (wake === sleep) {
    return [];
  }
  
  // Handle edge case where sleep time is midnight (00:00)
  if (sleep === 0) {
    sleep = MIDNIGHT_END;
  }
  
  // Handle case where wake time is after sleep time (normal schedule)
  if (wake > sleep) {
    return [{ start: sleep, end: wake }];
  }
  
  // Handle overnight schedule (sleep time is before wake time)
  // Handle edge cases with midnight boundaries
  if (sleep === MIDNIGHT_END) {
    return [{ start: MIDNIGHT_START, end: wake }];
  }
  
  if (wake === MIDNIGHT_START) {
    return [{ start: sleep, end: MIDNIGHT_END }];
  }
  
  // Return two periods: sleep->midnight and midnight->wake
  return [
    { start: sleep, end: MIDNIGHT_END },
    { start: MIDNIGHT_START, end: wake }
  ];
};

/**
 * Checks if a time period falls outside of sleep slots (i.e., is valid for scheduling)
 * @param {string} startTime - Start time in "HH:mm" format
 * @param {string} endTime - End time in "HH:mm" format
 * @param {string} wakeTime - Wake time in "HH:mm" format
 * @param {string} sleepTime - Sleep time in "HH:mm" format
 * @returns {{isValid: boolean, error: string}} Validation result and error message
 */
export const validateTimeAgainstSleepSlots = (startTime, endTime, wakeTime, sleepTime) => {
  let start = convertToMinutes(startTime);
  let end = convertToMinutes(endTime);
  const sleepSlots = createSleepSlots(wakeTime, sleepTime);
  
  // Handle overnight time period
  if (end < start) {
    end += 24 * 60;
  }
  
  // If there are no sleep slots, all times are valid
  if (sleepSlots.length === 0) {
    return { isValid: true, error: "" };
  }
  
  // Check against each sleep slot
  for (const slot of sleepSlots) {
    let slotStart = slot.start;
    let slotEnd = slot.end;
    
    // Adjust times for overnight comparison if needed
    if (slot.start === 0 && start > 12 * 60) {
      start -= 24 * 60;
      end -= 24 * 60;
    }
    
    // Check if time period overlaps with sleep slot
    const hasOverlap = (
      (start < slotEnd && end > slotStart) || // Partial overlap
      (start >= slotStart && end <= slotEnd)  // Complete containment
    );
    
    if (hasOverlap) {
      return {
        isValid: false,
        error: "Selected time is outside your wake/sleep schedule"
      };
    }
  }
  
  return { isValid: true, error: "" };
};

export const validateTimeSelection = (startTime, endTime, wakeTime, sleepTime, obligations) => {
  const slotValidation = validateTimeAgainstSleepSlots(startTime, endTime, wakeTime, sleepTime);
  
  if (!slotValidation.isValid) {
    return { error: slotValidation.error, warning: "" };
  }

  console.log("Start time", startTime, typeof startTime);
  console.log("End time", endTime, typeof endTime);
  console.log("Wake time", wakeTime, typeof wakeTime);
  console.log("Sleep time", sleepTime, typeof sleepTime);

  let start = convertToMinutes(startTime);
  let end = convertToMinutes(endTime);

  // Calculate duration of new obligation
  let newObligationDuration = end - start;

  // Calculate remaining time including existing obligations
  let remainingTime = calculateRemainingTime(wakeTime, sleepTime, obligations, []);

  // Check if new obligation exceeds remaining time
  if (newObligationDuration > remainingTime) {
    return { 
      error: `This obligation exceeds available time (${Math.floor(remainingTime / 60)}h ${remainingTime % 60}m remaining)`, 
      warning: "" 
    };
  }

  // Check for overlaps with existing obligations
  for (const obligation of obligations) {
    let oblStart = convertToMinutes(obligation.startTime);
    let oblEnd = convertToMinutes(obligation.endTime);

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