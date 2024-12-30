import { create } from 'zustand';

const useScheduleStore = create((set) => ({
  schedule: null,
  scheduleData: null,
  setSchedule: (schedule) => set({ schedule }),
  setScheduleData: (scheduleData) => set({ scheduleData }),
}));

export default useScheduleStore;