import { writable } from 'svelte/store';
import { api } from '$lib/api';
import type { Goal, Milestone } from '../models';

interface GoalsState {
    goals: Goal[];
    dueReminders: any[];
    loading: boolean;
    error: string | null;
}

function createGoalsStore() {
    const { subscribe, set, update } = writable<GoalsState>({
        goals: [],
        dueReminders: [],
        loading: false,
        error: null
    });

    async function loadGoals() {
        update(s => ({ ...s, loading: true, error: null }));
        try {
            const goals = await api.get('/goals');
            update(s => ({ ...s, goals: Array.isArray(goals) ? goals : [], loading: false }));
        } catch (err: unknown) {
            update(s => ({ 
                ...s, 
                error: err instanceof Error ? err.message : 'Failed to load goals', 
                loading: false 
            }));
        }
    }

    async function createGoal(goal: Partial<Goal>) {
        update(s => ({ ...s, error: null }));
        try {
            const newGoal = await api.post('/goals', goal);
            update(s => ({ ...s, goals: [...s.goals, newGoal] }));
            return newGoal;
        } catch (err: unknown) {
            update(s => ({ ...s, error: err instanceof Error ? err.message : 'Failed to create goal' }));
            throw err;
        }
    }

    async function updateGoal(id: string, goalUpdate: Partial<Goal>) {
        update(s => ({ ...s, error: null }));
        try {
            const updated = await api.put(`/goals/${id}`, goalUpdate);
            update(s => ({
                ...s,
                goals: s.goals.map(g => g.id === id ? updated : g)
            }));
        } catch (err: unknown) {
            update(s => ({ ...s, error: err instanceof Error ? err.message : 'Failed to update goal' }));
            throw err;
        }
    }

    async function deleteGoal(id: string) {
        update(s => ({ ...s, error: null }));
        try {
            await api.delete(`/goals/${id}`);
            update(s => ({
                ...s,
                goals: s.goals.filter(g => g.id !== id)
            }));
        } catch (err: unknown) {
            update(s => ({ ...s, error: err instanceof Error ? err.message : 'Failed to delete goal' }));
            throw err;
        }
    }

    async function addMilestone(goalId: string, milestone: Partial<Milestone>) {
        update(s => ({ ...s, error: null }));
        try {
            const newMilestone = await api.post(`/goals/${goalId}/milestones`, milestone);
            update(s => ({
                ...s,
                goals: s.goals.map(g => g.id === goalId ? { ...g, milestones: [...g.milestones, newMilestone] } : g)
            }));
        } catch (err: unknown) {
            update(s => ({ ...s, error: err instanceof Error ? err.message : 'Failed to add milestone' }));
            throw err;
        }
    }

    async function updateMilestone(goalId: string, milestoneId: string, milestoneUpdate: Partial<Milestone>) {
        update(s => ({ ...s, error: null }));
        try {
            const updated = await api.put(`/goals/${goalId}/milestones/${milestoneId}`, milestoneUpdate);
            update(s => ({
                ...s,
                goals: s.goals.map(g => g.id === goalId ? {
                    ...g,
                    milestones: g.milestones.map(m => m.id === milestoneId ? updated : m)
                } : g)
            }));
        } catch (err: unknown) {
            update(s => ({ ...s, error: err instanceof Error ? err.message : 'Failed to update milestone' }));
            throw err;
        }
    }

    async function deleteMilestone(goalId: string, milestoneId: string) {
        update(s => ({ ...s, error: null }));
        try {
            await api.delete(`/goals/${goalId}/milestones/${milestoneId}`);
            update(s => ({
                ...s,
                goals: s.goals.map(g => g.id === goalId ? {
                    ...g,
                    milestones: g.milestones.filter(m => m.id !== milestoneId)
                } : g)
            }));
        } catch (err: unknown) {
            update(s => ({ ...s, error: err instanceof Error ? err.message : 'Failed to delete milestone' }));
            throw err;
        }
    }

    async function loadDueReminders() {
        try {
            const dueReminders = await api.get('/reminders/due');
            update(s => ({ ...s, dueReminders: Array.isArray(dueReminders) ? dueReminders : [] }));
        } catch (err: unknown) {
            update(s => ({ 
                ...s, 
                error: err instanceof Error ? err.message : 'Failed to load due reminders',
                dueReminders: [] 
            }));
        }
    }

    async function executeReminderAction(reminderId: string, actionType: string, newDueAt?: string) {
        update(s => ({ ...s, error: null }));
        const payload: any = { action_type: actionType };
        if (newDueAt) payload.new_due_at = newDueAt;
        
        try {
            await api.post(`/reminders/${reminderId}/actions`, payload);
        } catch (err: unknown) {
            update(s => ({ ...s, error: err instanceof Error ? err.message : 'Failed to execute reminder action' }));
            throw err;
        }
        
        // Refresh state after successful action
        try {
            await Promise.all([loadDueReminders(), loadGoals()]);
        } catch (refreshErr: unknown) {
            update(s => ({ 
                ...s, 
                error: 'Action succeeded but failed to refresh data. Please reload.'
            }));
        }
    }

    return {
        subscribe,
        set,
        update,
        loadGoals,
        createGoal,
        updateGoal,
        deleteGoal,
        addMilestone,
        updateMilestone,
        deleteMilestone,
        loadDueReminders,
        executeReminderAction
    };
}

export const goalsStore = createGoalsStore();
