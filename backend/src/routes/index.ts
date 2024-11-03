import { Router } from 'express';
import { ChatOllama } from '@langchain/ollama';

const model = new ChatOllama({
    model: 'llama3.2',
    baseUrl: 'https://ollama.hacktx24.tech',
});

const index = Router();

index.get('/', (req, res) => {
    res.send('Hello world!');
});

index.post('/chat', async (req, res) => {
    console.log(req);
    const { prompt } = req.body;
    const response = await model.invoke(prompt);

    console.log(response);
    res.send(response);
});

export default index;