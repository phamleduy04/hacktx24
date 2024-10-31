import request from 'supertest';
import { app } from '../app';

describe('Error page', () => {
    it('should return 404 for non-existing page', async () => {
        const response = await request(app).get('/fake-page');
        expect(response.status).toBe(404);
    });
});