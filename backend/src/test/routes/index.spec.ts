import request from 'supertest';
import { app } from '../../app';

describe('GET /', () => {
    it('should return 200 OK', async () => {
        const response = await request(app).get('/');
        expect(response.status).toBe(200);
    });

    it('should return "Hello world!"', async () => {
        const response = await request(app).get('/');
        expect(response.text).toContain('Hello world!');
    });
});