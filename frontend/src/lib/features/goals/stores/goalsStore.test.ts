import { describe, it, expect, vi, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { api } from '$lib/api';
import { goalsStore } from './goalsStore';

vi.mock('$lib/api', () => ({
    api: {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn()
    }
}));

describe('goalsStore', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('updateGoal rejects when api.put fails and updates store error state', async () => {
        const error = new Error('Backend failure');
        vi.mocked(api.put).mockRejectedValueOnce(error);

        await expect(goalsStore.updateGoal('g1', { title: 'New' })).rejects.toThrow('Backend failure');

        const state = get(goalsStore);
        expect(state.error).toBe('Backend failure');
    });

    it('addMilestone rejects when api.post fails and updates store error state', async () => {
        const error = new Error('Milestone add failed');
        vi.mocked(api.post).mockRejectedValueOnce(error);

        await expect(goalsStore.addMilestone('g1', { title: 'M1' })).rejects.toThrow('Milestone add failed');

        const state = get(goalsStore);
        expect(state.error).toBe('Milestone add failed');
    });
});
