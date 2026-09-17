import { writable } from 'svelte/store';
import { api } from '$lib/api';
import type { Goal, Milestone } from '../models'; // We need to check these types

interface RemindersResponse {
    // Will define soon
}

function createGoalsStore() {
    const { subscribe, set, update } = writable<{
        goals: Goal[],
        dueReminders: any[],
        loading: boolean,
        error: string | null
    }>({
        goals: [],
        dueReminders: [],
        loading: false,
        error: null
    });

    return {
        subscribe,
        set,
        update,
        async loadGoals() {
            update(s => ({ ...s, loading: true, error: null }));
            try {
                const goals = await api.get('/goals/');
                update(s => ({ ...s, goals, loading: false }));
            } catch (err: any) {
                update(s => ({ ...s, error: err.message || 'Failed to load goals', loading: false }));
            }
        },
        async createGoal(goal: any) {
            const newGoal = await api.post('/goals/', goal);
            update(s => ({ ...s, goals: [...s.goals, newGoal] }));
            return newGoal;
        },
        async updateGoal(id: string, goalUpdate: any) {
            const updated = await api.put(`/goals/${id}`, goalUpdate);
            update(s => ({
                ...s,
                goals: s.goals.map(g => g.id === id ? updated : g)
            }));
        },
        async deleteGoal(id: string) {
            await api.delete(`/goals/${id}`);
            update(s => ({
                ...s,
                goals: s.goals.filter(g => g.id !== id)
            }));
        },
        async addMilestone(goalId: string, milestone: any) {
            const newMilestone = await api.post(`/goals/${goalId}/milestones/`, milestone);
            update(s => ({
                ...s,
                goals: s.goals.map(g => g.id === goalId ? { ...g, milestones: [...g.milestones, newMilestone] } : g)
            }));
        },
        async updateMilestone(goalId: string, milestoneId: string, milestoneUpdate: any) {
            const updated = await api.put(`/goals/${goalId}/milestones/${milestoneId}`, milestoneUpdate);
            update(s => ({
                ...s,
                goals: s.goals.map(g => g.id === goalId ? {
                    ...g,
                    milestones: g.milestones.map(m => m.id === milestoneId ? updated : m)
                } : g)
            }));
        },
        async deleteMilestone(goalId: string, milestoneId: string) {
            await api.delete(`/goals/${goalId}/milestones/${milestoneId}`);
            update(s => ({
                ...s,
                goals: s.goals.map(g => g.id === goalId ? {
                    ...g,
                    milestones: g.milestones.filter(m => m.id !== milestoneId)
                } : g)
            }));
        },
        async loadDueReminders() {
            try {
                const dueReminders = await api.get('/reminders/due');
                update(s => ({ ...s, dueReminders }));
            } catch (err: any) {
                console.error("Failed to load due reminders", err);
            }
        },
        async executeReminderAction(reminderId: string, actionType: string, newDueAt?: string) {
            const payload: any = { action_type: actionType };
            if (newDueAt) payload.new_due_at = newDueAt;
            
            await api.post(`/reminders/${reminderId}/actions`, payload);
            
            // After successful action, reload reminders and goals (in case milestone status changed)
            this.loadDueReminders();
            this.loadGoals();
        }
    };
}

export const goalsStore = createGoalsStore();
