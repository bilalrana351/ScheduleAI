export interface Task {
  name: string;
  duration: string;
}

export interface Obligation {
  name: string;
  startTime: string;
  endTime: string;
}

export interface ScheduleData {
  wakeTime: string;
  sleepTime: string;
  obligations: Obligation[];
  tasks: Task[];
}

export interface TempTask {
  name: string;
  duration: string;
  unit: 'minutes' | 'hours';
  error: string;
  naturalText?: string;
}

export interface TempObligation {
  name: string;
  startTime: string;
  endTime: string;
  error: string;
  warning: string;
}

export interface Message {
  type: 'bot' | 'user';
  content: string | JSX.Element;
} 