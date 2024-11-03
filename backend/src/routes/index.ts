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
	// console.log(req);

	try {
		const { prompt } = req.body;
		console.log(req.body, prompt);
		const response = await model.invoke(prompt);
		console.log(response.content);
		res.send(response.content);
	} catch (e) {
		console.error(e);
		res.status(500).send(e);
	}
});

export default index;
