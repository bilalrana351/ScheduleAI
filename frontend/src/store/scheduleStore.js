import { create } from 'zustand';

const useScheduleStore = create((set) => ({
  schedule: null,
  setSchedule: (schedule) => set({ schedule }),
}));

export default useScheduleStore; 